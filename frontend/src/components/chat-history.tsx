import { useChat } from "@/context/chat-context";
import { cn } from "@/lib/utils";
import { useEffect, useRef } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Response } from "./response";
import { Spinner } from "./ui/spinner";

export function ChatHistory() {
  const { chatHistory, isLoading } = useChat();
  const containerRef = useRef<HTMLDivElement | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // auto-scroll to bottom when messages change
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "auto" });
    } else {
      containerRef.current?.scrollTo({
        top: containerRef.current.scrollHeight,
      });
    }
  }, [chatHistory.length]);

  return (
    <div className="fixed h-[calc(100vh-11.5rem)] w-screen flex flex-col items-center z-20">
      <div className="w-full max-w-[800px] flex-1 min-h-0 flex flex-col relative">
        <div
          className={cn(
            chatHistory.length === 0 && "hidden",
            "absolute bottom-0 left-0 z-50 h-16 w-full pointer-events-none bg-gradient-to-t from-stone-950 to-transparent",
          )}
        />

        <div
          ref={containerRef}
          className="w-full z-20 flex-1 min-h-0 overflow-y-auto scroll-container flex flex-col items-center gap-3 py-4 px-2 pt-16 pb-16 relative"
        >
          <div className="w-full max-w-[800px] flex-1 min-h-0 flex flex-col gap-3">
            {chatHistory.map((message, index) => (
              <div
                key={index}
                className={cn(
                  "max-w-[90%] w-auto w-max rounded-xl rounded-tl-md p-2 text-stone-300/90 font-sans whitespace-pre-wrap break-words",
                  message.role === "user" &&
                    "ml-auto text-right rounded-tr-md bg-orange-800/80 text-stone-400",
                )}
              >
                <Response>{message.content}</Response>
              </div>
            ))}
            {isLoading && (
              <div className="rounded-full h-12 w-12 min-w-12 min-h-12 ring-2 ring-orange-700 p-2 flex justify-center items-center mt-4">
                <Spinner />
              </div>
            )}
            <div ref={bottomRef} className="min-h-20 h-20 w-full" />
          </div>
        </div>
      </div>
    </div>
  );
}
