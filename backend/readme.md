# GitHub Repo AI Agent

An intelligent AI-powered agent that explores GitHub repositories using a suite of specialized tools. Built with **FastAPI**, **OpenAI**, and custom **SpoonAI** tooling, this agent can:

- Retrieve repository metadata (stars, description, primary language)
- List top-level folders and key files
- Explore subdirectories with visual tree rendering
- Search code and filenames using GitHub’s code search API
- Fetch and preview file contents
- Answer natural language questions about codebases

Perfect for developers wanting to quickly understand unfamiliar repositories.

---

## 📁 Project Structure

- **`api.py`** – FastAPI application with `/api/ask_repo` endpoint for agent queries (stateless, per-request instantiation)
- **`main.py`** – Core logic, tool definitions, and CLI interface for interactive use
- **`run_server.py`** – Entry point to start the FastAPI server with Uvicorn

---

## 🛠️ Features & Tools

| Tool | Description |
|------|-------------|
| `github_repo_info` | Fetches repo metadata (description, stars, language) |
| `github_repo_tree` | Returns only top-level folders and key root files (`README.md`, `package.json`, etc.) |
| `github_subdir_tree` | Renders a visual file tree for a specific subdirectory (with size guard to prevent context overflow) |
| `github_file_fetcher` | Retrieves and previews file content (truncated for efficiency) |
| `github_code_search` | Searches code or filenames within the repository using GitHub’s search API |

All tools are built on `spoon_ai.tools.base.BaseTool` and integrated into a `SpoonReactAI` agent for reactive, step-by-step reasoning.

---

## ⚙️ Environment Variables

The application requires the following environment variables:

```env
OPENAI_KEY=your_openai_api_key
OPENAI_MODEL_NAME=gpt-4o  # or any compatible model
OPENAI_API_BASE_URL=https://api.openai.com/v1  # optional, for custom endpoints
GITHUB_API_KEY=your_github_personal_access_token
```

> 💡 **Note**: The GitHub API key must have appropriate scopes to access public (or private) repositories.

---

## 🚀 Running the Application

### 1. Install Dependencies

```bash
pip install fastapi uvicorn openai httpx aiohttp spoon-ai python-dotenv
```

> Replace `spoon-ai` with your actual package name if different.

### 2. Start the Server

```bash
python run_server.py
```

The API will be available at `http://localhost:8000`.

### 3. (Optional) Use CLI Mode

For interactive exploration:

```bash
python main.py
```

Then ask questions like:
> "Explain how Cal.com handles authentication"

---

## 🌐 API Usage

### Endpoint

`POST /api/ask_repo`

### Request Body (JSON)

```json
{
  "user_prompt": "Where is the auth logic in this repo?",
  "repo_name": "calcom/cal.com",
  "chat_history": [
    {
      "role": "user",
      "content": "What does this repo do?"
    },
    {
      "role": "assistant",
      "content": "It's an open-source alternative to Calendly..."
    }
  ]
}
```

### Response

```json
{
  "user_prompt": "Where is the auth logic in this repo?",
  "agent_response": "Authentication is handled in the `apps/web/lib/auth` directory using NextAuth.js..."
}
```

### CORS

CORS is enabled for:
- `http://localhost:3003`
- `http://127.0.0.1:3000`

Modify `origins` in `api.py` as needed.

---

## 🔒 Security & Best Practices

- **Stateless Design**: A new agent instance is created per request to avoid cross-talk.
- **Context Truncation**: File and directory outputs are aggressively limited to preserve token budget.
- **Error Handling**: Clear error messages for missing env vars or GitHub API failures.
- **No Short-Term Memory**: Disabled for API mode to ensure reproducibility.

---

## 🧪 Example Workflow

1. User asks: “How does this repo handle user sessions?”
2. Agent uses `github_repo_tree` → sees `apps/web`
3. Uses `github_subdir_tree` on `apps/web` → finds `lib/auth`
4. Uses `github_code_search` for `filename:auth.ts`
5. Fetches relevant files with `github_file_fetcher`
6. Synthesizes findings via OpenAI into a concise answer

---

## 📄 License

MIT License — see `LICENSE` for details.

---

## 🙌 Acknowledgements

- Powered by **OpenAI** and **GitHub API**
- Built using the **SpoonAI** framework for agentic reasoning
- Inspired by developer workflows for rapid codebase comprehension
