import { sleep } from "@/lib/utils";
import React, { createContext, type PropsWithChildren, use } from "react";
import { toast } from "sonner";

type ChatContextVal = {
  isLoading: boolean;
  isError: boolean;
  chatHistory: ChatMessage[];
  sendMessage: (val: string, query: string) => Promise<boolean>;
};
type Props = PropsWithChildren<{}>;

const ChatContext = createContext<ChatContextVal | null>(null);

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export function ChatProvider({ children }: Props) {
  const [chatHistory, setChatHistory] = React.useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [isError, setIsError] = React.useState(false);

  async function sendMessage(repo: string, query: string) {
    let error_case = false;
    try {
      setIsError(false);
      setIsLoading(true);
      setChatHistory((prev) => [...prev, { role: "user", content: query }]);

      const res = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/ask_repo`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_prompt: query,
            repo_name: repo,
            chat_history: chatHistory,
          }),
        },
      );

      if (!res.ok) {
        toast.error("Failed to send message");
        throw new Error("Failed to send message");
      }

      const response = await res.json();

      if (response.error) {
        toast.error(response.error);
        throw new Error("Failed to ");
      }
      setChatHistory((prev) => [
        ...prev,
        { role: "assistant", content: response.agent_response },
      ]);
    } catch (error) {
      setIsError(true);
      // toast.error("Failed to send message");
      console.error(error);
      error_case = true;
    } finally {
      setIsLoading(false);
    }
    return error_case;
  }

  return (
    <ChatContext value={{ chatHistory, sendMessage, isLoading, isError }}>
      {children}
    </ChatContext>
  );
}

export function useChat() {
  const val = use(ChatContext);
  if (!val) throw new Error("useTheme called outside of ThemeProvider!");
  return val;
}
