from typing import Dict, List,Any, Optional
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool,tool
from datetime import datetime
import requests
import os
import re

# def save_to_file(content: str, filename: str = "research_output.txt") -> str:
#     """Saves content to a file with a timestamped filename."""
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     fromated_txt = f"---Research Output - {timestamp}---\n\n{content}\n\n---End of Research Output---"
#     # full_filename = f"{timestamp}_{filename}"
#     with open(filename,"a",encoding="utf-8") as file:
#         file.write(fromated_txt)
#     return f"Content saved to {filename}"

# save_tool = Tool(
#     name="save_to_file",
#     func=save_to_file,
#     description="Saves the provided content to a text file and returns the filename."
# )

# search=DuckDuckGoSearchRun()
# search_tool = Tool(
#     name="Search",
#     func=search.run,
#     description="Search the web for information."
# )


# https://searxng.deepseek.ai/

@tool("searxng_search", return_direct=False)
def searxng_search(query: str, api_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Search the web or a SearXNG instance specifically for legal texts and documents 
    related to the Egyptian Civil Law (Sanhuri Law / كتاب السنهوري).

    This tool is designed to assist research in Egyptian civil law by providing 
    relevant articles, principles, and explanations from official documents, 
    legal commentaries, and online resources.

    Args:
        query (str): The search query in Arabic or English, e.g., 
                     "المادة 147 القانون المدني السنهوري القوة الملزمة".
        api_url (Optional[str]): The base URL of the SearXNG instance. 
                                 If None, defaults to the `SEARXNG_URL` environment variable 
                                 or a public instance (`https://search.snopyta.org`).

    Returns:
        Dict[str, Any]: A dictionary containing a nested 'output' key for compatibility with 
                        the chatbot agent. The inner 'output' key contains:
                        - 'results': a list of dictionaries with 'title', 'url', and 'snippet' of each document
                        - or an 'error' message if no results are found or a network issue occurs.
    """
    api_url = "https://google.com"

    try:
        response = requests.get(
            f"{api_url}/search",
            params={"q": query, "format": "json"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        results_raw: List[Dict[str, Any]] = data.get("results", [])

        if not results_raw:
            return {"output": {"output": "No results found."}}

        formatted_results: List[Dict[str, str]] = []
        for result in results_raw[:5]:
            formatted_results.append({
                "title": result.get("title", "No Title"),
                "url": result.get("url", "No URL"),
                "snippet": result.get("content", "No Snippet")
            })

        return {"output": {"output": formatted_results}}

    except requests.exceptions.RequestException as e:
        return {"output": {"output": f"Error during search: {str(e)}"}}

search_tool=searxng_search
# search_tool=Tool(
#     name="search_tool",
#     func=search_tool,
#     description="Search the web for information using SearXNG instance."
# )

# wiki = WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=1000)
# wiki_tool = WikipediaQueryRun(api_wrapper=wiki)


# try:
#     import docx
# except ImportError:
#     docx = None

# try:
#     import fitz  # PyMuPDF for PDFs
# except ImportError:
#     fitz = None


# def read_sanhuri_book(file_path: str="sample.txt", chunk_size: int = 2000, overlap: int = 200) -> list[dict]:
#     """
#     Reads, cleans, and splits the Sanhuri book for LLM engine processing.

#     Supports .txt, .pdf, and .docx files.
#     Returns a list of chunks with metadata ready for embeddings or model input.

#     Args:
#         file_path (str): Path to the Sanhuri book file.
#         chunk_size (int): Size of each text chunk.
#         overlap (int): Number of overlapping characters between chunks.

#     Returns:
#         list[dict]: [{"content": <chunk_text>, "metadata": {...}}, ...]
#     """

#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"File not found: {file_path}")

#     ext = os.path.splitext(file_path)[-1].lower()

#     if ext == ".txt":
#         with open(file_path, "r", encoding="utf-8") as f:
#             print("The programing reading the text file")
#             text = f.read()
#         # print(text)
#     elif ext == ".pdf":
#         if not fitz:
#             raise ImportError("Please install PyMuPDF: pip install pymupdf")
#         text = ""
#         with fitz.open(file_path) as doc:
#             for page in doc:
#                 text += page.get_text("text") + "\n"
#     elif ext == ".docx":
#         if not docx:
#             raise ImportError("Please install python-docx: pip install python-docx")
#         doc = docx.Document(file_path)
#         text = "\n".join([p.text for p in doc.paragraphs])
#     else:
#         raise ValueError(f"Unsupported file type: {ext}")

#     # --- Clean text ---
#     # print("Cleaing text")
#     text = re.sub(r'\s+', ' ', text)               # normalize spaces
#     text = re.sub(r'\[\d+\]|\(\d+\)', '', text)    # remove footnotes/numbers
#     text = text.replace('\u200f', '')              # remove Arabic RTL marks
#     text = text.strip()
#     # print(text)
#     # --- Split into overlapping chunks ---
#     # print("Overlapping chunks that is prepared by text ")
#     chunks = []
#     start = 0
#     while start < len(text):
#         end = start + chunk_size
#         chunk = text[start:end].strip()
#         chunks.append({
#             "content": chunk,
#             "metadata": {
#                 "source": os.path.basename(file_path),
#                 "chunk_start": start,
#                 "chunk_end": min(end, len(text))
#             }
#         })
#         start += chunk_size - overlap
#     # print(chunks)
#     return chunks

# @Tool("read_sanhuri_book", return_direct=False)

# def read_tool(file_path: str = "sample.txt") -> str:
#     """
#     A tool that allows the LLM to read and access the Sanhuri law book.
#     It reads the book, preprocesses it, and returns the first few chunks of text.
#     """
#     try:
#         chunks = read_sanhuri_book(file_path)
#         # You can limit the size if it’s huge:
#         preview = "\n\n".join([c["content"] for c in chunks[:3]])
#         return f"Successfully read {len(chunks)} chunks from {file_path}.\n\nPreview:\n{preview[:1500]}"
#     except Exception as e:
#         return f"Error reading Sanhuri book: {e}"

# read_tool=Tool(
#     name="Read_tool",
#     func=read_tool,
#     description="Read tool for using Sanhuri Law book to answer given values"
# )

# # read_sanhuri_book()
