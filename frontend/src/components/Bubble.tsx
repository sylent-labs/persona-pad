import { useEffect, useRef, useState } from "react";

type BubbleRole = "user" | "persona";

interface BubbleProps {
  role: BubbleRole;
  text: string;
  /** True when this bubble is the last in its role-streak; renders the iMessage tail. */
  tail?: boolean;
  /** True when this bubble starts a new sender streak (controls top spacing). */
  lead?: boolean;
  variant?: "default" | "error";
  label?: string;
}

export function Bubble({
  role,
  text,
  tail = false,
  lead = false,
  variant = "default",
  label,
}: BubbleProps) {
  const rowClass = [
    "bubble-row",
    `bubble-row--${role}`,
    lead ? "bubble-row--lead" : "",
  ]
    .filter(Boolean)
    .join(" ");

  const bubbleClass = [
    "bubble",
    `bubble--${role}`,
    tail ? "bubble--tail" : "",
    variant === "error" ? "bubble--error" : "",
  ]
    .filter(Boolean)
    .join(" ");

  const showCopy = variant !== "error";
  const copyButton = showCopy ? <CopyButton text={text} /> : null;

  return (
    <div className={rowClass}>
      {role === "user" ? copyButton : null}
      <div className={bubbleClass}>
        {label ? <span>{label}</span> : null}
        {text}
      </div>
      {role === "persona" ? copyButton : null}
    </div>
  );
}

interface CopyButtonProps {
  text: string;
}

function CopyButton({ text }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  async function handleClick() {
    try {
      await navigator.clipboard?.writeText(text);
      setCopied(true);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard may be unavailable (insecure context, etc.) — fail silently.
    }
  }

  const className = ["bubble-copy", copied ? "bubble-copy--copied" : ""]
    .filter(Boolean)
    .join(" ");

  return (
    <button
      type="button"
      className={className}
      onClick={handleClick}
      aria-label={copied ? "Copied" : "Copy message"}
      title={copied ? "Copied" : "Copy"}
    >
      {copied ? <CheckIcon /> : <CopyIcon />}
    </button>
  );
}

function CopyIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

export function TypingBubble() {
  return (
    <div className="bubble-row bubble-row--persona bubble-row--lead">
      <div
        className="bubble bubble--persona bubble--tail bubble--typing"
        aria-label="typing"
      >
        <span />
        <span />
        <span />
      </div>
    </div>
  );
}
