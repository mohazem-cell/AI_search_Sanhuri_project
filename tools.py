from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime
import os
import re

def save_to_file(content: str, filename: str = "research_output.txt") -> str:
    """Saves content to a file with a timestamped filename."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fromated_txt = f"---Research Output - {timestamp}---\n\n{content}\n\n---End of Research Output---"
    # full_filename = f"{timestamp}_{filename}"
    with open(filename,"a",encoding="utf-8") as file:
        file.write(fromated_txt)
    return f"Content saved to {filename}"

save_tool = Tool(
    name="save_to_file",
    func=save_to_file,
    description="Saves the provided content to a text file and returns the filename."
)

# search=DuckDuckGoSearchRun()
# search_tool = Tool(
#     name="Search",
#     func=search.run,
#     description="Search the web for information."
# )

# wiki = WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=1000)
# wiki_tool = WikipediaQueryRun(api_wrapper=wiki)


try:
    import docx
except ImportError:
    docx = None

try:
    import fitz  # PyMuPDF for PDFs
except ImportError:
    fitz = None


def read_sanhuri_book(file_path: str="sample.txt", chunk_size: int = 2000, overlap: int = 200) -> list[dict]:
    """
    Reads, cleans, and splits the Sanhuri book for LLM engine processing.

    Supports .txt, .pdf, and .docx files.
    Returns a list of chunks with metadata ready for embeddings or model input.

    Args:
        file_path (str): Path to the Sanhuri book file.
        chunk_size (int): Size of each text chunk.
        overlap (int): Number of overlapping characters between chunks.

    Returns:
        list[dict]: [{"content": <chunk_text>, "metadata": {...}}, ...]
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            print("The programing reading the text file")
            text = f.read()
        # print(text)
    elif ext == ".pdf":
        if not fitz:
            raise ImportError("Please install PyMuPDF: pip install pymupdf")
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    elif ext == ".docx":
        if not docx:
            raise ImportError("Please install python-docx: pip install python-docx")
        doc = docx.Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # --- Clean text ---
    # print("Cleaing text")
    text = re.sub(r'\s+', ' ', text)               # normalize spaces
    text = re.sub(r'\[\d+\]|\(\d+\)', '', text)    # remove footnotes/numbers
    text = text.replace('\u200f', '')              # remove Arabic RTL marks
    text = text.strip()
    # print(text)
    # --- Split into overlapping chunks ---
    # print("Overlapping chunks that is prepared by text ")
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        chunks.append({
            "content": chunk,
            "metadata": {
                "source": os.path.basename(file_path),
                "chunk_start": start,
                "chunk_end": min(end, len(text))
            }
        })
        start += chunk_size - overlap
    # print(chunks)
    return chunks

@Tool("read_sanhuri_book", return_direct=False)

def read_tool(file_path: str = "sample.txt") -> str:
    """
    A tool that allows the LLM to read and access the Sanhuri law book.
    It reads the book, preprocesses it, and returns the first few chunks of text.
    """
    try:
        chunks = read_sanhuri_book(file_path)
        # You can limit the size if it’s huge:
        preview = "\n\n".join([c["content"] for c in chunks[:3]])
        return f"Successfully read {len(chunks)} chunks from {file_path}.\n\nPreview:\n{preview[:1500]}"
    except Exception as e:
        return f"Error reading Sanhuri book: {e}"

read_tool=Tool(
    name="Read_tool",
    func=read_tool,
    description="Read tool for using Sanhuri Law book to answer given values"
)

# read_sanhuri_book()
