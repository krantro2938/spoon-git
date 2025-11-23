import asyncio
import base64
import os
from typing import Any, Dict, List

import aiohttp
import httpx
from openai import AsyncOpenAI
from spoon_ai.agents import SpoonReactAI
from spoon_ai.chat import ChatBot
from spoon_ai.tools.base import BaseTool


# -----------------------------
# Helper: Build visual tree from filtered paths (with line limit)
# -----------------------------
def build_visual_tree_from_paths(
    tree_data: List[Dict[str, Any]], base_path: str = ""
) -> str:
    from collections import defaultdict

    base_parts = base_path.strip("/").split("/") if base_path else []
    base_depth = len(base_parts)

    dirs = defaultdict(list)
    for item in tree_data:
        path = item["path"]
        if base_path and not path.startswith(base_path):
            continue
        parts = path.split("/")
        rel_parts = parts[base_depth:] if base_depth > 0 else parts
        if not rel_parts:
            continue
        parent = "/".join(rel_parts[:-1]) if len(rel_parts) > 1 else ""
        dirs[parent].append(
            {"name": rel_parts[-1], "type": item["type"], "size": item.get("size")}
        )

    def _render_dir(current_path: str = "", level: int = 0) -> List[str]:
        indent = "│   " * level
        lines = []
        children = sorted(
            dirs.get(current_path, []), key=lambda x: (x["type"] != "tree", x["name"])
        )
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            connector = "└── " if is_last else "├── "
            icon = "📁 " if child["type"] == "tree" else "📄 "
            size_info = f" ({child['size']} bytes)" if child.get("size") else ""
            line = f"{indent}{connector}{icon}{child['name']}{size_info}"
            lines.append(line)
            if child["type"] == "tree":
                next_path = (
                    f"{current_path}/{child['name']}".strip("/")
                    if current_path
                    else child["name"]
                )
                lines.extend(_render_dir(next_path, level + 1))
        return lines

    lines = _render_dir()
    if len(lines) > 80:
        lines = lines[:80] + ["... (truncated to save context)"]
    return "\n".join(lines) if lines else "📁 (empty directory)"


# -----------------------------
# GitHub Code Search Tool
# -----------------------------
class GitHubCodeSearchTool(BaseTool):
    name: str = "github_code_search"
    description: str = "Search for code or filenames in a GitHub repository."
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query (e.g., 'filename:DateRangeHeader.tsx')",
            },
            "repo": {"type": "string", "description": "Repo in 'owner/name' format"},
        },
        "required": ["query", "repo"],
    }

    async def execute(self, query: str, repo: str, **kwargs):
        url = "https://api.github.com/search/code"
        headers = {
            "Authorization": f"token {os.environ['GITHUB_API_KEY']}",
            "Accept": "application/vnd.github.v3+json",
        }
        full_query = f"{query} repo:{repo}"
        async with httpx.AsyncClient() as client:
            r = await client.get(
                url, headers=headers, params={"q": full_query, "per_page": 10}
            )
            if r.status_code == 200:
                data = r.json()
                results = []
                for item in data.get("items", []):
                    results.append(
                        {
                            "name": item["name"],
                            "path": item["path"],
                            "url": item["html_url"],
                        }
                    )
                return (
                    {"results": results} if results else {"error": "No matches found."}
                )
            else:
                return {"error": f"Search failed: {r.status_code} {r.text}"}


# -----------------------------
# GitHub File Fetcher Tool (aggressive truncation)
# -----------------------------
class GitHubFileFetcherTool(BaseTool):
    name: str = "github_file_fetcher"
    description: str = "Fetch a preview of a specific file (max 2000 chars)."
    parameters: dict = {
        "type": "object",
        "properties": {
            "owner": {"type": "string"},
            "repo": {"type": "string"},
            "file_path": {"type": "string"},
            "branch": {"type": "string", "default": "main"},
        },
        "required": ["owner", "repo", "file_path"],
    }

    async def execute(
        self, owner: str, repo: str, file_path: str, branch: str = "main", **kwargs
    ):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
        headers = {
            "Authorization": f"token {os.environ['GITHUB_API_KEY']}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                if data["type"] == "file":
                    content = base64.b64decode(data["content"]).decode("utf-8")
                    preview = content
                    # if len(content) > 2000:
                    #     preview += "\n... (truncated)"
                    return {
                        "path": file_path,
                        "content_preview": preview,
                    }
            return {"error": f"File '{file_path}' not found."}


# -----------------------------
# GitHub Repo Info Tool
# -----------------------------
class GitHubRepoInfoTool(BaseTool):
    name: str = "github_repo_info"
    description: str = "Get repo metadata (stars, description, etc.)."
    parameters: dict = {
        "type": "object",
        "properties": {
            "owner": {"type": "string"},
            "repo": {"type": "string"},
        },
        "required": ["owner", "repo"],
    }

    async def execute(self, owner: str, repo: str, **kwargs):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {  # ⭐️ ADD THIS BLOCK
            "Authorization": f"token {os.environ['GITHUB_API_KEY']}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                return {
                    "full_name": data.get("full_name"),
                    "description": data.get("description"),
                    "stars": data.get("stargazers_count"),
                    "language": data.get("language"),
                }


# -----------------------------
# GitHub Root Tree Tool (only top-level folders)
# -----------------------------
def build_visual_tree_limited(tree_data: List[Dict[str, Any]]) -> str:
    # Extract only root-level directories and key files
    root_dirs = set()
    root_files = []
    for item in tree_data:
        path = item["path"]
        if "/" not in path:
            if item["type"] == "tree":
                root_dirs.add(path)
            else:
                if path in {"README.md", "package.json", "pnpm-lock.yaml", "yarn.lock"}:
                    root_files.append(path)
    # Build simple list
    lines = []
    for d in sorted(root_dirs):
        lines.append(f"📁 {d}")
    for f in sorted(root_files):
        lines.append(f"📄 {f}")
    if len(lines) > 80:
        lines = lines[:80] + ["... (truncated)"]
    return "\n".join(lines)


class GitHubRepoTreeTool(BaseTool):
    name: str = "github_repo_tree"
    description: str = "Get top-level folders and key files only."
    parameters: dict = {
        "type": "object",
        "properties": {
            "owner": {"type": "string"},
            "repo": {"type": "string"},
            "branch": {"type": "string", "default": "main"},
        },
        "required": ["owner", "repo"],
    }

    async def execute(self, owner: str, repo: str, branch: str = "main", **kwargs):
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        headers = {  # ⭐️ ADD THIS BLOCK
            "Authorization": f"token {os.environ['GITHUB_API_KEY']}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=headers)
            if r.status_code != 200:
                return {"error": "Failed to fetch repo structure."}
        tree = r.json().get("tree", [])
        visual = build_visual_tree_limited(tree)
        return f"Top-level structure of {owner}/{repo}:\n\n{visual}"


# -----------------------------
# GitHub Subdirectory Tree Tool (with size guard)
# -----------------------------
class GitHubSubdirTreeTool(BaseTool):
    name: str = "github_subdir_tree"
    description: str = "Get tree for a subdirectory (e.g., 'apps/web')."
    parameters: dict = {
        "type": "object",
        "properties": {
            "owner": {"type": "string"},
            "repo": {"type": "string"},
            "subdir": {"type": "string"},
            "branch": {"type": "string", "default": "main"},
        },
        "required": ["owner", "repo", "subdir"],
    }

    async def execute(
        self, owner: str, repo: str, subdir: str, branch: str = "main", **kwargs
    ):
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        headers = {
            "Authorization": f"token {os.environ['GITHUB_API_KEY']}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=headers)
            if r.status_code != 200:
                return {"error": "Failed to fetch repo structure."}
        full_tree = r.json().get("tree", [])

        prefix = subdir.strip("/") + "/"
        filtered = [
            item
            for item in full_tree
            if item["path"] == subdir or item["path"].startswith(prefix)
        ]

        if not filtered:
            return {"error": f"Directory '{subdir}' not found."}

        if len(filtered) > 500:
            return {
                "error": f"Directory '{subdir}' is too large. Please request a specific file instead."
            }

        visual = build_visual_tree_from_paths(filtered, base_path=subdir)
        return f"Contents of {owner}/{repo}/{subdir}:\n\n{visual}"


# -----------------------------
# Main
# -----------------------------
async def main():
    agent = SpoonReactAI(
        llm=ChatBot(
            use_llm_manager=True,
            llm_provider="openai",
            base_url=os.environ.get("OPENAI_API_BASE_URL"),
            api_key=os.environ["OPENAI_KEY"],
            model_name=os.environ.get("OPENAI_MODEL_NAME"),  # must support tools
            enable_short_term_memory=True,
        ),
        tools=[
            GitHubRepoInfoTool(),
            GitHubRepoTreeTool(),
            GitHubSubdirTreeTool(),
            GitHubFileFetcherTool(),
            GitHubCodeSearchTool(),
        ],
    )

    print("🤖 GitHub Repo AI — Smart, step-by-step exploration")
    print('Try: "Explain how Cal.com handles authentication"\n')
    print("Type 'exit' to quit.")

    system_message = (
        "<SYSTEM PROMPT"
        "You are an expert software engineer helping users understand GitHub repositories. "
        "Prioritize correctness and efficiency. Avoid guessing file paths. If a file isn’t found, try a broader search or infer from nearby files."
        "When you finished, always respond with a summary or answer to the users question."
        "</SYSTEM PROMPT>"
    )

    openai_client = AsyncOpenAI(
        api_key=os.environ["OPENAI_KEY"],
        base_url=os.environ.get("OPENAI_API_BASE_URL", "https://api.openai.com/v1"),
    )

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye! 👋")
            break

        try:
            response = await agent.run(system_message + user_input)

            if any(
                phrase in response
                for phrase in [
                    "Thinking completed",
                    "No action needed",
                    "Task finished",
                ]
            ):
                final_prompt = (
                    "You are an expert software engineer. Based on the following observations from GitHub tools, "
                    "provide a clear, concise answer to the user's question.\n\n"
                    f"User question: {user_input}\n\n"
                    f"Tool observations:\n{response}\n\n"
                    "Answer:"
                )

                # ✅ Direct OpenAI call
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

            print(f"\nAI: {response}")
        except Exception as e:
            print(f"\n⚠️ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
