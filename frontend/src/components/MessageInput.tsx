import { useLayoutEffect, useRef, useState } from "react";

interface MessageInputProps {
  onSend: (text: string) => void;
  disabled: boolean;
}

/**
 * The composer pill: a decorative attach glyph, an auto-grow textarea, and the
 * gradient send button. Mode selection lives in the Tone card (desktop) and the
 * mode chips row (mobile), not here.
 */
export function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const trimmed = text.trim();
  const sendDisabled = disabled || trimmed.length === 0;

  // Auto-grow the textarea to fit its content. CSS max-height caps the height
  // and switches to scrolling.
  useLayoutEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }, [text]);

  function submit() {
    if (sendDisabled) return;
    onSend(trimmed);
    setText("");
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    submit();
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  }

  return (
    <form className="composer" onSubmit={handleSubmit}>
      <span className="composer__attach" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
          <path d="M12 5v14M5 12h14" />
        </svg>
      </span>
      <textarea
        ref={textareaRef}
        className="composer__field"
        aria-label="Message"
        rows={1}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
      />
      <button
        type="submit"
        className="composer__send"
        aria-label="Send"
        disabled={sendDisabled}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M12 19V5" />
          <path d="M5 12l7-7 7 7" />
        </svg>
      </button>
    </form>
  );
}
