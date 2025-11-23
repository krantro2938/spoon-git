import React, { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Textarea } from "./ui/textarea";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import {
  CheckIcon,
  ChevronDownIcon,
  Github,
  PlusIcon,
  SendIcon,
  TrashIcon,
} from "lucide-react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { toast } from "sonner";
import { useChat } from "@/context/chat-context";
import { Spinner } from "./ui/spinner";
import { cn } from "@/lib/utils";

const STORAGE_KEY = "my_repos_v1";
const DEFAULT_REPOS = ["calcom/cal.com", "golang/go", "rust-lang/rust"];

type StoredShape = {
  repos: string[];
  selected?: string;
};

export function UserInput() {
  const { sendMessage, isLoading, chatHistory } = useChat();
  const [inputValue, setInputValue] = useState("");
  const [selectedRepo, setSelectedRepo] = useState<string>(DEFAULT_REPOS[0]);
  const [newRepo, setNewRepo] = useState("");
  const [repos, setRepos] = useState<string[]>(DEFAULT_REPOS);

  const modalRef = useRef<HTMLDivElement | null>(null);
  const [translateY, setTranslateY] = useState<number>(0);
  const GAP = 4; // px gap from bottom

  const computeTranslateToBottom = () => {
    const el = modalRef.current;
    if (!el) return 0;
    const vw = window.innerHeight;
    const rect = el.getBoundingClientRect();
    const modalHeight = rect.height;
    const centeredTop = (vw - modalHeight) / 2;
    const desiredTop = vw - modalHeight - GAP;
    return Math.max(0, desiredTop - centeredTop);
  };

  useLayoutEffect(() => {
    if (chatHistory.length === 0) {
      setTranslateY(0);
      return;
    }
    requestAnimationFrame(() => {
      setTranslateY(computeTranslateToBottom());
    });
  }, [chatHistory.length]);

  useEffect(() => {
    const onResize = () => {
      setTranslateY((prev) => {
        if (chatHistory.length === 0) return 0;
        return computeTranslateToBottom();
      });
    };
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [chatHistory.length]);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        const initial: StoredShape = {
          repos: DEFAULT_REPOS,
          selected: DEFAULT_REPOS[0],
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
        setRepos(DEFAULT_REPOS);
        setSelectedRepo(DEFAULT_REPOS[0]);
        return;
      }
      const parsed = JSON.parse(raw) as StoredShape;
      if (parsed && Array.isArray(parsed.repos) && parsed.repos.length > 0) {
        setRepos(parsed.repos);
        const sel =
          parsed.selected && parsed.repos.includes(parsed.selected)
            ? parsed.selected
            : parsed.repos[0];
        setSelectedRepo(sel);
      } else {
        const initial: StoredShape = {
          repos: DEFAULT_REPOS,
          selected: DEFAULT_REPOS[0],
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
        setRepos(DEFAULT_REPOS);
        setSelectedRepo(DEFAULT_REPOS[0]);
      }
    } catch (e) {
      const initial: StoredShape = {
        repos: DEFAULT_REPOS,
        selected: DEFAULT_REPOS[0],
      };
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
      } catch {}
      setRepos(DEFAULT_REPOS);
      setSelectedRepo(DEFAULT_REPOS[0]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    try {
      const payload: StoredShape = { repos, selected: selectedRepo };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    } catch {}
  }, [repos, selectedRepo]);

  function addRepo(repoName: string) {
    const trimmed = repoName.trim();
    if (trimmed === "" || repos.includes(trimmed) || !trimmed.includes("/")) {
      toast.warning("Please enter a valid repository name");
      return;
    }
    setNewRepo("");
    setRepos((prev) => {
      const next = [...prev, trimmed];
      setSelectedRepo(trimmed);
      return next;
    });
  }

  function setRepo(repoName: string) {
    setSelectedRepo(repoName);
  }

  function removeRepo(repoName: string) {
    setRepos((prev) => {
      const next = prev.filter((r) => r !== repoName);
      setSelectedRepo((current) => {
        if (current === repoName) {
          return next.length > 0 ? next[0] : "";
        }
        return current;
      });
      return next;
    });
    toast.success("Repository removed");
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
                        key={repo}
                        className="group text-stone-300 p-2 flex items-center justify-between text-sm cursor-pointer hover:bg-stone-900 rounded-md"
                      >
                        <div
                          className="flex items-center gap-2 flex-1"
                          onClick={() => setRepo(repo)}
                        >
                          <span className="truncate">{repo}</span>
                          {repo === selectedRepo && (
                            <CheckIcon className="text-orange-600" size={16} />
                          )}
                        </div>

                        <button
                          onClick={() => removeRepo(repo)}
                          className="cursor-pointer opacity-0 group-hover:opacity-100 transition-opacity duration-150 text-stone-400 hover:text-red-500 ml-3"
                          aria-label={`Remove ${repo}`}
                          title={`Remove ${repo}`}
                        >
                          <TrashIcon size={16} />
                        </button>
                      </div>
                    ))}
                    {repos.length === 0 && (
                      <div className="text-stone-400 text-sm p-2">
                        No repositories. Add one above.
                      </div>
                    )}
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
                  e.preventDefault();
                  handleSubmit();
                }
              }}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask the AI about the selected GitHub repository..."
              className=" flex-1 rounded-2xl p-4 min-h-28 max-h-28 border-none resize-none focus-visible:ring-0 focus-visible:ring-offset-0 overflow-y-auto leading-relaxed  bg-black text-stone-400"
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
