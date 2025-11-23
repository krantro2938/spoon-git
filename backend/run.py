import asyncio
import base64
import os
from typing import Any, Dict, List

import aiohttp
import httpx
from spoon_ai.agents import SpoonReactAI
from spoon_ai.chat import ChatBot
from spoon_ai.tools.base import BaseTool


# -----------------------------
# GitHub File Fetcher Tool
# -----------------------------
class GitHubFileFetcherTool(BaseTool):
    async def execute(
        self, owner: str, repo: str, file_path: str, branch: str = "main"
    ):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            if r.status_code == 200:
                data = r.json()
                if data["type"] == "file":
                    content = base64.b64decode(data["content"]).decode("utf-8")
                    return {
                        "path": file_path,
                        "content": content[:8000],
                    }  # truncate if needed
            return {"error": "File not found or too large"}


# -----------------------------
# GitHub Repo Info Tool
# -----------------------------
class GitHubRepoInfoTool(BaseTool):
    name: str = "github_repo_info"
    description: str = "Fetch information about a GitHub repository, including stars."
    parameters: dict = {
        "type": "object",
        "properties": {
            "owner": {"type": "string"},
            "repo": {"type": "string"},
        },
        "required": ["owner", "repo"],
    }

    async def execute(self, owner: str, repo: str):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return {
                    "full_name": data.get("full_name"),
                    "description": data.get("description"),
                    "stars": data.get("stargazers_count"),
                    "forks": data.get("forks_count"),
                    "open_issues": data.get("open_issues_count"),
                    "language": data.get("language"),
                    "url": data.get("html_url"),
                }


# -----------------------------
# GitHub Repo Tree Tool
# -----------------------------


def build_visual_tree(
    tree_data: List[Dict[str, Any]], max_files_per_dir: int = 10
) -> str:
    """Build a human-readable visual tree from GitHub tree data."""
    # Group paths by directory
    from collections import defaultdict

    dirs = defaultdict(list)
    for item in tree_data:
        path = item["path"]
        parts = path.split("/")
        parent = "/".join(parts[:-1]) if len(parts) > 1 else ""
        dirs[parent].append(
            {"name": parts[-1], "type": item["type"], "size": item.get("size")}
        )

    def _render_dir(prefix: str, current_path: str, level: int = 0) -> List[str]:
        indent = "│   " * level
        lines = []

        children = sorted(
            dirs.get(current_path, []), key=lambda x: (x["type"] != "tree", x["name"])
        )

        # Optional: limit files shown per dir to avoid explosion
        if len(children) > max_files_per_dir:
            visible = children[:max_files_per_dir]
            extra_count = len(children) - max_files_per_dir
        else:
            visible = children
            extra_count = 0

        for i, child in enumerate(visible):
            is_last = i == len(visible) - 1 and extra_count == 0
            connector = "└── " if is_last else "├── "
            icon = "📁 " if child["type"] == "tree" else "📄 "
            size_info = f" ({child['size']} bytes)" if child.get("size") else ""
            line = f"{indent}{connector}{icon}{child['name']}{size_info}"
            lines.append(line)

            if child["type"] == "tree":
                next_path = f"{current_path}/{child['name']}".strip("/")
                lines.extend(_render_dir(prefix, next_path, level + 1))

        if extra_count > 0:
            lines.append(f"{indent}└── ... (+{extra_count} more files/dirs)")

        return lines

    root_lines = _render_dir("", "", 0)
    return "\n".join(root_lines)


class GitHubRepoTreeTool(BaseTool):
    name: str = "github_repo_tree"
    description: str = (
        "Get a visual file tree of a GitHub repo (like Unix `tree` command)."
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "owner": {"type": "string"},
            "repo": {"type": "string"},
            "branch": {"type": "string", "default": "main"},
        },
        "required": ["owner", "repo"],
    }

    async def execute(self, owner: str, repo: str, branch: str = "main"):
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            r.raise_for_status()
        tree = r.json().get("tree", [])

        visual_tree = build_visual_tree(tree)
        return (
            f"Repository tree for {owner}/{repo} (branch: {branch}):\n\n{visual_tree}"
        )


# -----------------------------
# Main Chat Loop (with custom provider)
# -----------------------------
async def main():
    agent = SpoonReactAI(
        llm=ChatBot(
            use_llm_manager=True,
            llm_provider="openai",
            base_url=os.environ["OPENAI_API_BASE_URL"],
            api_key=os.environ["OPENAI_KEY"],
            model_name=os.environ["OPENAI_MODEL_NAME"],
            enable_short_term_memory=True,
        ),
        tools=[GitHubRepoInfoTool(), GitHubRepoTreeTool()],
    )

    print("🤖 GitHub Repo AI — type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye! 👋")
            break

        try:
            response = await agent.run(user_input)
            print(f"\nAI: {response}")
        except Exception as e:
            print(f"\n⚠️ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
