from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field, ValidationError
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from anthropic import BadRequestError
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
# from tools import search_tool,wiki_tool,save_tool
# from tools import read_tool
# from langchain.agents import create_openai_functions_agent
from tools import search_tool

load_dotenv()


class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str] 

# llm=ChatOpenAI(model="gpt-4o-mini")

# llm2 = ChatOpenAI(
#     model="deepseek-chat",
#     api_key=os.getenv("DEEPSEEK_API_KEY"),
#     base_url="https://openrouter.ai/api/v1",
# )
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found. Please set it in your .env file or environment variables.")
# print("dfiejefiejfiejfiejfiejifiefiejfie")

llm2 = ChatOpenAI(
    model="openai/gpt-oss-20b",
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key,
    temperature=0
)

# print("Loaded key:", os.getenv("ANTHROPIC_API_KEY"))  # check if it's loaded

parser = PydanticOutputParser(pydantic_object=ResearchResponse)

response = llm2.invoke("What is the capital of France?")
print(response.content)

# prompt = ChatPromptTemplate.from_messages([
#     ("system", """
#         You are a research assistent that will help generate a research paper. 
#         Answer the user query and use neccessary tools.
#         Wrap the output in this format and provide no other text:
#         \n{format_instructions}.
#     """),
#     ("placeholder", "{chat_history}"),
#     ("human", "{Query}"),
#     ("placeholder", "{agent_scratchpad}")
# ]).partial(format_instructions=parser.get_format_instructions())

prompt = ChatPromptTemplate.from_messages([
    ("system", """
        You are a research assistent that will help generate a research paper. 
        Answer the user query and use only given tools.
        Wrap the output in this format and provide no other text:
        \n{format_instructions}.
    """),
    ("placeholder", "{chat_history}"),
    ("human", "{Query}"),
    ("placeholder", "{agent_scratchpad}")
]).partial(format_instructions=parser.get_format_instructions())

# tools=[search_tool,wiki_tool,save_tool]
tools=[search_tool]
agent = create_tool_calling_agent(
    llm=llm2,
    tools=tools,
    prompt=prompt
    # output_parser=parser
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
)
while True:
    query = input("What can I help you? ")
    if query.lower() in ["exit","quit","q"]:
        break
    raw_response = agent_executor.invoke({"Query": query})

    try:
        # structured_response = parser.parse(raw_response.get("output",raw_response)["output"])
        structured_response = parser.parse(raw_response.get("output", raw_response)["output"])

        print(structured_response)
        print("\n---------------------------------------------------------------------------\n")

    except Exception as e:
        print("Error parsing response:", e, "Raw response",raw_response)

# raw_response = agent_executor.invoke({"Query": "Provide a detailed search about Egyptian history."})
# print("Raw response:", raw_response)