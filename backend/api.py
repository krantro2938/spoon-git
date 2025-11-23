# api.py
import os
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from pydantic import BaseModel

from main import (
    ChatBot,
    GitHubCodeSearchTool,
    GitHubFileFetcherTool,
    GitHubRepoInfoTool,
    GitHubRepoTreeTool,
    GitHubSubdirTreeTool,
    SpoonReactAI,
)

app = FastAPI(
    title="GitHub Repo AI Agent",
    description="An AI agent that explores GitHub repositories using specialized tools.",
)

origins_str = os.environ.get("ALLOWED_CORS_ORIGINS")

if origins_str:
    origins = [o.strip() for o in origins_str.split(",")]
else:
    origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HistoryMessage(BaseModel):
    role: str
    content: str


class AgentQuery(BaseModel):
    user_prompt: str
    repo_name: str
    chat_history: list[HistoryMessage]


# --- Agent Initialization ---
# This function is executed once when the app starts.
def initialize_agent():
    """Initializes and returns the SpoonReactAI agent."""
    openai_key = os.environ.get("OPENAI_KEY")
    if not openai_key:
        raise ValueError("OPENAI_KEY environment variable not set.")

    llm_chatbot = ChatBot(
        use_llm_manager=True,
        llm_provider="openai",
        base_url=os.environ.get("OPENAI_API_BASE_URL"),
        api_key=openai_key,
        model_name=os.environ.get("OPENAI_MODEL_NAME"),
        enable_short_term_memory=False,  # Using False for stateless API calls
    )

    return SpoonReactAI(
        llm=llm_chatbot,
        tools=[
            GitHubRepoInfoTool(),
            GitHubRepoTreeTool(),
            GitHubSubdirTreeTool(),
            GitHubFileFetcherTool(),
            GitHubCodeSearchTool(),
        ],
    )


# --- Global Agent Instance (for simplicity) ---
# try:
#     AGENT = initialize_agent()
# except ValueError as e:
#     # Handle missing environment variables during startup
#     print(f"Agent initialization error: {e}")
#     AGENT = None

LLM_CHATBOT_CONFIG = {
    "use_llm_manager": True,
    "llm_provider": "openai",
    "base_url": os.environ.get("OPENAI_API_BASE_URL"),
    "api_key": os.environ.get("OPENAI_KEY"),
    "model_name": os.environ.get("OPENAI_MODEL_NAME"),
    "enable_short_term_memory": False,
}

TOOL_INSTANCES = [
    GitHubRepoInfoTool(),
    GitHubRepoTreeTool(),
    GitHubSubdirTreeTool(),
    GitHubFileFetcherTool(),
    GitHubCodeSearchTool(),
]


# --- Agent Factory Function (Run PER REQUEST) ---
def create_new_agent_instance() -> Optional[SpoonReactAI]:
    """Creates a fresh SpoonReactAI instance using pre-initialized components."""
    openai_key = os.environ.get("OPENAI_KEY")
    if not openai_key:
        return None

    llm_chatbot = ChatBot(**LLM_CHATBOT_CONFIG)

    return SpoonReactAI(llm=llm_chatbot, tools=TOOL_INSTANCES)


# --- API Endpoint ---
@app.post("/api/ask_repo", tags=["Agent"])
async def ask_repo_agent(query: AgentQuery):
    """
    Sends a query to the AI agent to explore a GitHub repository.
    """
    agent = create_new_agent_instance()

    if agent is None:
        return {"error": "Agent not initialized due to configuration error"}, 500

    system_message = (
        "You are an expert software engineer helping users understand GitHub repositories. "
        "Prioritize correctness and efficiency. Avoid guessing file paths. If a file isn’t found, try a broader search or infer from nearby files."
        "When you finished, always respond with a summary or answer to the users question."
        "This is the repository you are exploring: " + query.repo_name
    )

    full_conversation_prompt = f"<SYSTEM_PROMPT>{system_message}</SYSTEM_PROMPT>\n\n"

    for message in query.chat_history:
        if message.role == "user":
            full_conversation_prompt += f"USER: {message.content}\n"
        elif message.role == "assistant":
            full_conversation_prompt += f"ASSISTANT: {message.content}\n"

    full_conversation_prompt += f"USER: {query.user_prompt}"

    try:
        response = await agent.run(full_conversation_prompt)

        if any(
            phrase in response
            for phrase in [
                "Thinking completed",
                "No action needed",
                "Task finished",
            ]
        ):
            openai_client = AsyncOpenAI(
                api_key=os.environ["OPENAI_KEY"],
                base_url=os.environ.get(
                    "OPENAI_API_BASE_URL", "https://api.openai.com/v1"
                ),
            )

            final_prompt = (
                "You are an expert software engineer. Based on the following observations from GitHub tools, "
                "provide a clear, concise answer to the user's question.\n\n"
                f"User question: {query.user_prompt}\n\n"
                f"Tool observations:\n{response}\n\n"
                "Answer:"
            )

            completion = await openai_client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL_NAME", "gpt-4o"),
                messages=[
                    {
                        "role": "system",
                        "content": "You answer technical questions about codebases precisely and concisely.",
                    },
                    {"role": "user", "content": final_prompt},
                ],
                temperature=0.0,
                max_tokens=500,
            )
            response = completion.choices[0].message.content

        return {"user_prompt": query.user_prompt, "agent_response": response}

    except Exception as e:
        return {"error": f"An error occurred during agent execution: {e}"}, 500


@app.get("/healthz", tags=["Status"])
async def healthz():
    """
    Health check endpoint. Returns a 200 OK status
    to indicate the application is running and responsive.
    """
    return {"status": "ok", "message": "Service is running"}
