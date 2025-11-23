# Youtube link
[YouTube](https://www.youtube.com/watch?v=5TJU-lM4tVo)

# GitHub Repo AI Agent

An intelligent, full-stack AI application designed to explore, analyze, and explain GitHub repositories. This tool combines a powerful Python-based AI agent with a modern, reactive web interface to help developers quickly understand unfamiliar codebases.

---

## 🚀 Project Overview

This project allows users to input a GitHub repository URL and ask natural language questions about it. The system uses an AI agent equipped with specialized tools to navigate the repository's file structure, read code, and synthesize answers.

### Key Capabilities
- **Repository Exploration**: Visualize file trees and directory structures.
- **Code Analysis**: Search for specific code patterns or filenames.
- **Contextual Q&A**: Ask questions like "How does authentication work?" or "Where is the API entry point?" and get cited answers.
- **Interactive UI**: A chat-based interface for seamless interaction with the agent.

---

## 🏗️ Architecture

The project is divided into two main components:

### 1. [Backend](./backend)
The brain of the operation. A **FastAPI** server that hosts the AI agent.
- **Tech**: Python, FastAPI, OpenAI, SpoonAI.
- **Features**: Custom tools for GitHub API interaction, stateless agent design, and context management.
- 📖 **[Read Backend Documentation](./backend/readme.txt)**

### 2. [Frontend](./frontend)
The user interface. A modern web application built with **TanStack Start**.
- **Tech**: React 19, TanStack Start, Vite, Tailwind CSS v4.
- **Features**: Real-time chat interface, markdown rendering, and responsive design.
- 📖 **[Read Frontend Documentation](./frontend/README.md)**

---

## 🏁 Quick Start

To run the full stack locally, you will need to start both the backend and frontend servers.

1. **Setup Backend**:
   Navigate to the `backend` directory, install dependencies, and start the FastAPI server.
   *(See [Backend README](./backend/readme.txt) for detailed instructions)*

2. **Setup Frontend**:
   Navigate to the `frontend` directory, install dependencies, and start the Vite dev server.
   *(See [Frontend README](./frontend/README.md) for detailed instructions)*

---

## 📄 License

MIT License.
