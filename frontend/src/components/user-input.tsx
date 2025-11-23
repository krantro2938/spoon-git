import React, { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Textarea } from "./ui/textarea";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import {
  CheckIcon,
  ChevronDownIcon,
  Github,
  Plus,
  PlusIcon,
  SendIcon,
} from "lucide-react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { toast } from "sonner";
import { useChat } from "@/context/chat-context";
import { Spinner } from "./ui/spinner";
import { cn, sleep } from "@/lib/utils";

export function UserInput() {
  const { sendMessage, isLoading, chatHistory, isError } = useChat();
  const [inputValue, setInputValue] = React.useState("");
  const [selectedRepo, setSelectedRepo] = React.useState("calcom/cal.com");
  const [newRepo, setNewRepo] = useState("");
  const [repos, setRepos] = useState<string[]>([
    "calcom/cal.com",
    "golang/go",
    "rust-lang/rust",
  ]);

  const modalRef = useRef<HTMLDivElement | null>(null);
  const [translateY, setTranslateY] = useState<number>(0);
  const GAP = 4; // px gap from bottom

  // compute translation needed to move the modal from centered to bottom gap
  const computeTranslateToBottom = () => {
    const el = modalRef.current;
    if (!el) return 0;
    const vw = window.innerHeight;
    const rect = el.getBoundingClientRect();
    const modalHeight = rect.height;
    // current top when centered (we assume modal is centered by flex on the overlay)
    const centeredTop = (vw - modalHeight) / 2;
    // desired top so modal bottom is GAP pixels above viewport bottom
    const desiredTop = vw - modalHeight - GAP;
    // delta to apply as translateY (px)
    return Math.max(0, desiredTop - centeredTop);
  };

  // Update translation when history changes and when resized
  useLayoutEffect(() => {
    // only apply when there's at least one message (you can adjust condition)
    if (chatHistory.length === 0) {
      setTranslateY(0);
      return;
    }
    // compute on next frame so layout is stable
    requestAnimationFrame(() => {
      setTranslateY(computeTranslateToBottom());
    });
  }, [chatHistory.length]);

  useEffect(() => {
    const onResize = () => {
      // recalc so the animation target remains accurate on resize
      setTranslateY((prev) => {
        // if currently at 0 and no history, keep 0
        if (chatHistory.length === 0) return 0;
        return computeTranslateToBottom();
      });
    };
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [chatHistory.length]);

  function addRepo(repoName: string) {
    if (
      repoName === "" ||
      repos.includes(repoName) ||
      !repoName.includes("/")
    ) {
      toast.warning("Please enter a valid repository name");
      return;
    }
    setNewRepo("");
    setRepos((prev) => [...prev, repoName]);
  }

  function setRepo(repoName: string) {
    setSelectedRepo(repoName);
  }

  async function handleSubmit() {
    const res = await sendMessage(selectedRepo, inputValue);
    if (!res) {
      setInputValue("");
    }
  }

  return (
    <div
      className={cn(
        "fixed inset-0 flex items-center justify-center z-10",
        chatHistory.length === 0 && "z-30",
      )}
    >
      {/* modal wrapper — transform is transitioned so it animates smoothly */}
      <div
        ref={modalRef}
        className={cn(
          "mx-auto w-full max-w-[800px] rounded-2xl transition-transform duration-400 ease-out",
        )}
        style={{
          maxHeight: "80vh",
          overflow: "hidden",
          transform: `translateY(${translateY}px)`,
        }}
      >
        <div className="p-0.5 rounded-2xl bg-orange-950 w-full max-w-[800px] mb-4">
          <div className="p-2 flex justify-end">
            <Popover>
              <PopoverTrigger className="cursor-pointer text-[10px] text-stone-300 flex gap-3 items-center p-2 bg-stone-950 rounded-full">
                <Github className="text-orange-500" size={14} /> {selectedRepo}
                <ChevronDownIcon size={14} />
              </PopoverTrigger>
              <PopoverContent
                side="bottom"
                className="p-0 border-none ring-none bg-transparent"
              >
                <div className="flex flex-col gap-2 bg-black p-2 rounded-xl">
                  <div className="flex gap-3">
                    <Input
                      value={newRepo}
                      onChange={(e) => setNewRepo(e.target.value)}
                      placeholder="Add a new repository..."
                      className="border-stone-800 focus:border-stone-800 text-stone-300 focus:outline-none outline-none ring-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-stone-800 bg-transparent"
                    />
                    <Button
                      onClick={() => addRepo(newRepo)}
                      className="bg-stone-900 hover:bg-stone-900/80 cursor-pointer"
                    >
                      <PlusIcon className="text-stone-400" />
                    </Button>
                  </div>
                  <div>
                    {repos.map((repo) => (
                      <div
                        className="text-stone-300 p-2 flex justify-between text-sm cursor-pointer hover:bg-stone-900 rounded-md"
                        onClick={() => {
                          setRepo(repo);
                        }}
                      >
                        {repo}
                        {repo === selectedRepo && (
                          <CheckIcon className="text-orange-600" size={16} />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </PopoverContent>
            </Popover>
          </div>
          <div className="relative">
            <Textarea
              value={inputValue}
              disabled={isLoading}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault(); // Prevent newline
                  handleSubmit();
                }
              }}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask the AI about the selected GitHub repository..."
              className=" flex-1 rounded-2xl p-4 min-h-28 border-none resize-none focus-visible:ring-0 focus-visible:ring-offset-0 overflow-y-auto leading-relaxed  bg-black text-stone-400"
            />
            <Button
              onClick={() => handleSubmit()}
              disabled={inputValue === "" || isLoading}
              className={
                "absolute bottom-2 right-2 bg-orange-800 text-stone-300 hover:bg-orange-800/80 cursor-pointer"
              }
            >
              {isLoading ? <Spinner className="animate-spin" /> : <SendIcon />}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
