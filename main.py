from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field, ValidationError
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from anthropic import BadRequestError
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool
import json

load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str] 

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found. Please set it in your .env file or environment variables.")

def ask_sanhuri(query: str) -> str:
    # Placeholder function to simulate searching Sanhuri Law documents

    llm2 = ChatOpenAI(
        model="openai/gpt-oss-20b",
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
        temperature=0
    )

    parser = PydanticOutputParser(pydantic_object=ResearchResponse)

    # response = llm2.invoke("What is the capital of France?")
    # print(response.content)

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
    )

    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
    )
    # while True:
        # if query.lower() in ["exit","quit","q"]:
        #     break
    raw_response = agent_executor.invoke({"Query": query})

    # raw_output = raw_response.get("output")  # this is a JSON string
    # if isinstance(raw_output, str):
    #     raw_output = json.loads(raw_output)  # now it becomes a dict

    # structured_response = parser.parse(raw_output)
    try:
        # structured_response = parser.parse(raw_response.get("output",raw_response)["output"])
        structured_response = parser.parse(raw_response["output"])
        # print(structured_response)
        # structured_response = parser.parse(raw_output)
        # print(structured_response)
        return structured_response
    except Exception as e:
        print("Error parsing response:", e, "Raw response",raw_response)

# query = input("How can I help you? ")
# ask_sanhuri(query)
