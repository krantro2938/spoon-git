# Code Spoon Frontend

A modern, reactive frontend interface for the **GitHub Repo AI Agent**. This application allows developers to interactively explore GitHub repositories, ask questions about codebases, and visualize file structures through a chat-based UI.

Built with **React 19**, **Vite**, and **TanStack Start**.

---

## ✨ Features

- **Interactive Chat Interface**: Natural language queries about any public GitHub repository.
- **Markdown Rendering**: Rich text support for AI responses, including code blocks with syntax highlighting.
- **Responsive Design**: Clean, modern UI built with Tailwind CSS v4 and Radix UI primitives.
- **Real-time Feedback**: Loading states, error handling via toast notifications (Sonner).
- **History Management**: Maintains chat context for follow-up questions.

---

## 🛠️ Tech Stack

- **Framework**: [TanStack Start](https://tanstack.com/start)
- **Core Library**: [React 19](https://react.dev/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Routing**: [TanStack Router](https://tanstack.com/router)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
- **UI Components**: [Radix UI](https://www.radix-ui.com/) & [Lucide React](https://lucide.dev/)
- **Markdown**: `react-markdown`, `react-syntax-highlighter`, `remark-gfm`
- **State Management**: React Context API

---

## 🚀 Getting Started

### Prerequisites

- Node.js (v18+) or [Bun](https://bun.sh/) (recommended)
- A running instance of the [Backend API](../backend/README.md)

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   bun install
   ```

### Environment Variables

Create a `.env` file in the `frontend` directory (or copy `.env.example` if available) and configure the backend URL:

```env
VITE_BACKEND_URL=http://localhost:8000
```

> **Note**: Ensure this matches the URL where your FastAPI backend is running.

### Running the Development Server

Start the development server:

```bash
npm run dev
# or
bun dev
```

The application will be available at `http://localhost:3000`.

---

## 📁 Project Structure

```
frontend/
├── public/             # Static assets
├── src/
│   ├── components/     # Reusable UI components (Chat, UI primitives)
│   ├── context/        # React Context providers (ChatContext)
│   ├── lib/            # Utility functions
│   ├── routes/         # TanStack Router definitions
│   ├── styles.css      # Global styles and Tailwind directives
│   └── router.tsx      # Router configuration
├── package.json        # Dependencies and scripts
├── tsconfig.json       # TypeScript configuration
└── vite.config.ts      # Vite configuration
```

---

## 🧪 Scripts

- `dev`: Start the development server
- `build`: Build the application for production
- `serve`: Preview the production build locally
- `test`: Run tests using Vitest

---

## 🤝 Integration

This frontend is designed to work seamlessly with the **SpoonAI Backend**. It sends requests to the `/api/ask_repo` endpoint, handling the streaming of repository information and AI-generated answers.

For more details on the backend architecture, please refer to the [Backend README](../backend/readme.txt).