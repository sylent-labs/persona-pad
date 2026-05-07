type BubbleRole = "user" | "persona";

interface BubbleProps {
  role: BubbleRole;
  text: string;
  /** True when this bubble is the last in its role-streak; renders the iMessage tail. */
  tail?: boolean;
  /** True when this bubble starts a new sender streak (controls top spacing). */
  lead?: boolean;
  variant?: "default" | "error";
}

export function Bubble({
  role,
  text,
  tail = false,
  lead = false,
  variant = "default",
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

  return (
    <div className={rowClass}>
      <div className={bubbleClass}>{text}</div>
    </div>
  );
}

export function TypingBubble() {
  return (
    <div className="bubble-row bubble-row--persona bubble-row--lead">
      <div className="bubble bubble--persona bubble--tail bubble--typing" aria-label="typing">
        <span />
        <span />
        <span />
      </div>
    </div>
  );
}
