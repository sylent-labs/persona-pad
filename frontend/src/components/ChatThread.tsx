import { useEffect, useRef } from "react";

import type { Mode } from "../api/types";
import { MODES } from "../api/types";
import type { ChatMessage, PersonaMessage } from "../types";
import { Bubble, TypingBubble } from "./Bubble";

interface ChatThreadProps {
  messages: ChatMessage[];
  pending: boolean;
  error: string | null;
}

function modeLabel(mode: Mode): string {
  return MODES.find((m) => m.value === mode)?.label ?? mode;
}

export function ChatThread({ messages, pending, error }: ChatThreadProps) {
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, pending]);

  return (
    <div className="thread">
      {messages.map((msg, idx) => {
        if (msg.role === "user") {
          const isLast = idx === messages.length - 1;
          const delivered = isLast && !pending && !error;
          return (
            <div key={msg.id} className="thread__turn">
              <Bubble role="user" text={msg.text} />
              {delivered ? <div className="thread__delivered">Delivered</div> : null}
            </div>
          );
        }
        return <PersonaBlock key={msg.id} message={msg} />;
      })}

      {pending ? (
        <div className="thread__turn">
          <PersonaHeader mode={null} />
          <TypingBubble />
        </div>
      ) : null}

      {error ? (
        <div className="thread__turn">
          <PersonaHeader mode={null} />
          <Bubble role="persona" text={error} variant="error" />
        </div>
      ) : null}

      <div ref={endRef} />
    </div>
  );
}

interface PersonaBlockProps {
  message: PersonaMessage;
}

function PersonaBlock({ message }: PersonaBlockProps) {
  const hasAlternate = message.alternate.trim().length > 0;
  return (
    <div className="thread__turn">
      <PersonaHeader mode={message.mode} />

      <div className="option">
        <div className="option__label">Option 1</div>
        <Bubble role="persona" text={message.draft} />
      </div>

      {hasAlternate ? (
        <div className="option">
          <div className="option__label">Option 2</div>
          <Bubble role="persona" text={message.alternate} />
        </div>
      ) : null}
    </div>
  );
}

interface PersonaHeaderProps {
  /** The mode the draft was generated with; null while typing/erroring. */
  mode: Mode | null;
}

function PersonaHeader({ mode }: PersonaHeaderProps) {
  return (
    <div className="persona-header">
      <span className="persona-header__avatar" aria-hidden="true">VK</span>
      <span className="persona-header__name">Van Keith</span>
      {mode ? <span className="persona-header__pill">{modeLabel(mode)}</span> : null}
    </div>
  );
}
