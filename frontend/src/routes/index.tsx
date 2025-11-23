import { ChatHistory } from "@/components/chat-history";
import { Input } from "@/components/ui/input";
import { UserInput } from "@/components/user-input";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <div className="bg-black font-mono h-screen w-screen overflow-hidden text-white relative">
      <ChatHistory />
      <UserInput />
    </div>
  );
}
