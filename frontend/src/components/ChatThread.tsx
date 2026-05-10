import { useEffect, useRef } from "react";

import type { ChatMessage } from "../types";
import { Bubble, TypingBubble } from "./Bubble";

interface ChatThreadProps {
  messages: ChatMessage[];
  pending: boolean;
  error: string | null;
  emptyHint: string;
}

export function ChatThread({
  messages,
  pending,
  error,
  emptyHint,
}: ChatThreadProps) {
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, pending]);

  if (messages.length === 0 && !pending && !error) {
    return (
      <div className="chat-thread chat-thread__empty">
        <div>{emptyHint}</div>
      </div>
    );
  }

  return (
    <div className="chat-thread">
      {messages.map((msg, idx) => {
        const prev = messages[idx - 1];
        const next = messages[idx + 1];
        const isLastBubble =
          idx === messages.length - 1 || (next && next.role !== msg.role);
        const isLeadBubble = !prev || prev.role !== msg.role;
        const showDelivered =
          msg.role === "user" &&
          idx === messages.length - 1 &&
          !pending &&
          !error;

        return (
          <div key={msg.id}>
            <Bubble
              role={msg.role}
              text={msg.text}
              tail={Boolean(isLastBubble)}
              lead={isLeadBubble}
              label={msg.label ?? ""}
            />
            {showDelivered ? (
              <div className="chat-thread__delivered">Delivered</div>
            ) : null}
          </div>
        );
      })}
      {pending ? <TypingBubble /> : null}
      {error ? (
        <Bubble role="persona" text={error} tail lead variant="error" />
      ) : null}
      <div ref={endRef} />
    </div>
  );
}
