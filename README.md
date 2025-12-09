# LangGraph Video Script Generator

This project is an AI-powered video script generator built with [LangGraph](https://github.com/langchain-ai/langgraph). It automates the process of researching a topic and generating a professional video script, using two main nodes:
- **Research Node:** Searches the web for relevant information.
- **Screenwriting Node:** Writes a video script based on the research.

Scripts are generated in DOCX format and can be integrated with Notion for content management.

---

## Features

- Automated web research and script writing using AI (OpenAI via LangChain, Tavily)
- FastAPI backend with endpoints for script generation, status tracking, and download
- Notion integration for saving scripts to your Notion workspace
- DOCX output for easy editing and sharing
- Rate limiting and API key authentication

---

## Installation

### 1. Prerequisites

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) (a fast Python package manager and virtual environment tool)

### 2. Clone the repository

```bash
git clone <your-repo-url>
cd langgraph_project
```

### 3. Install uv

Follow the [official uv installation guide](https://docs.astral.sh/uv/install/):

```bash
# For macOS (Homebrew)
brew install astral-sh/uv/uv

# Or use pipx
pipx install uv
```

### 4. Create a virtual environment and install dependencies

```bash
uv venv
source .venv/bin/activate  # or .venv/Scripts/activate on Windows
uv pip install -r requirements.txt
```

### 5. Set up environment variables

Copy the example environment file and fill in your API keys and configuration:

```bash
cp .env.example .env
```

Edit `.env` and provide your actual credentials.

#### Example `.env.example`:

```
# API authentication
HEADER_API_KEY=changeme

# Notion integration
NOTION_TOKEN=your-notion-integration-token
NOTION_DB_ID=your-notion-database-id

# OpenAI API (for language model)
OPENAI_API_KEY=your-openai-api-key

# Tavily API (for web search)
TAVILY_API_KEY=your-tavily-api-key

# Model selection (optional, defaults to gpt-4o-mini)
MODEL=gpt-4o-mini
```

---

## Usage

Start the FastAPI server with Uvicorn:

```bash
uvicorn src.api:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000).

### Endpoints

- `POST /generate-script` — Generate a new video script
- `GET /task/{task_id}` — Check the status of a script generation task
- `GET /download-script/{task_id}` — Download the generated script (DOCX)
- `GET /health` — Health check

All endpoints require the `X-API-KEY` header with your `HEADER_API_KEY` value.

---

## Contributing

This project is primarily for personal use, but contributions are welcome! Please open an issue or submit a pull request if you have suggestions or improvements.

---

## License

This project is licensed under the MIT License.

---

## Troubleshooting

- Make sure all required API keys are set in your `.env` file.
- If you encounter issues with uv, refer to the [official uv documentation](https://docs.astral.sh/uv/).
- For FastAPI/Uvicorn issues, see the [FastAPI docs](https://fastapi.tiangolo.com/) and [Uvicorn docs](https://www.uvicorn.org/).

---

Let me know if you want to add or change anything!