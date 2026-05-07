import { useState } from "react";

import type { Mode } from "../api/types";
import { MODES } from "../api/types";

interface MessageInputProps {
  onSend: (text: string) => void;
  mode: Mode;
  onModeChange: (mode: Mode) => void;
  disabled: boolean;
}

export function MessageInput({ onSend, mode, onModeChange, disabled }: MessageInputProps) {
  const [text, setText] = useState("");
  const trimmed = text.trim();
  const sendDisabled = disabled || trimmed.length === 0;

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (sendDisabled) return;
    onSend(trimmed);
    setText("");
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (sendDisabled) return;
      onSend(trimmed);
      setText("");
    }
  }

  return (
    <>
      <div
        className="mode-chips"
        role="radiogroup"
        aria-label="Reply mode"
      >
        {MODES.map((m) => (
          <button
            key={m.value}
            type="button"
            role="radio"
            aria-checked={m.value === mode}
            className={
              "mode-chip" + (m.value === mode ? " mode-chip--active" : "")
            }
            onClick={() => onModeChange(m.value)}
          >
            {m.label}
          </button>
        ))}
      </div>
      <form className="message-input" onSubmit={handleSubmit}>
        <label className="message-input__field">
          <textarea
            aria-label="Message"
            placeholder="Message"
            rows={1}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
          />
        </label>
        <button
          type="submit"
          className="message-input__send"
          aria-label="Send"
          disabled={sendDisabled}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M12 19V5" />
            <path d="M5 12l7-7 7 7" />
          </svg>
        </button>
      </form>
    </>
  );
}
