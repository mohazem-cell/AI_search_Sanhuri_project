# AI_search_Sanhuri_project
This project is an AI-powered search assistant that leverages multiple tools and large language models (LLMs) to provide comprehensive search results and summaries. It integrates with Searxng for web searches and Groq for advanced language processing.

## Quick start — make the project run

1. Create and activate a virtual environment (or use the provided `myenv`):
   - Linux / macOS:
     ```
     source myenv/bin/activate
     ```
   - Windows (PowerShell):
     ```
     python3.11 -m venv myenv
     .\myenv\Scripts\activate
     ```

2. Install dependencies:
   ```
   uv pip install -r requirements.txt --link-mode=copy
   ```
3. Configure environment variables:
    - Create a .env file in the project root (this file is ignored by git per .gitignore).
    - Required:
      GROQ_API_KEY — API key used by ask_sanhuri.
    - Optional:
      OPENAI_API_KEY, ANTHROPIC_API_KEY, SEARXNG_URL — when using other providers or a custom SearxNG instance.
4. Start the API server:
   ```
    uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --reload   
    ```
5. Call the service:
    - GET:
    ```
    http://localhost:8000/search?query=(your+search+terms)
    ```
    - Post:
    ```
    curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" \
      -d '{"query":"(your+search+terms+output)"}'
    ```

6. How it works (brief)
    - The FastAPI app exposes endpoints that call ask_sanhuri.
    - ask_sanhuri creates an LLM-backed agent and calls the configured tools (for example, search_tool) to gather web results and then formats the output into the ResearchResponse pydantic model.
    - The web-search tool implementation lives in tools.py. If you run into web-search issues, confirm SEARXNG_URL or update the searxng_search implementation.
    