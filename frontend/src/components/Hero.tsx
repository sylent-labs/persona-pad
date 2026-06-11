import type { QuickAction } from "../quickActions";
import { SuggestionCards } from "./SuggestionCards";

interface HeroProps {
  onQuickAction: (action: QuickAction) => void;
  disabled: boolean;
}

/** Welcome / empty state: AI-core orb, heading, suggestion cards. */
export function Hero({ onQuickAction, disabled }: HeroProps) {
  return (
    <div className="hero">
      <AiCoreOrb />
      <h1 className="hero__heading">What can I help you?</h1>
      <SuggestionCards onQuickAction={onQuickAction} disabled={disabled} />
    </div>
  );
}

/**
 * The glowing AI core: a hexagon outline + ring framing a gradient rounded
 * square "+" chip. The ambient glow behind it is hand-coded CSS.
 */
function AiCoreOrb() {
  return (
    <div className="orb" aria-hidden="true">
      <div className="orb__glow" />
      <svg className="orb__frame" viewBox="0 0 120 120" fill="none">
        <path
          d="M60 6 105 32 105 88 60 114 15 88 15 32Z"
          stroke="var(--border-strong)"
          strokeWidth="1.5"
        />
        <circle cx="60" cy="60" r="40" stroke="var(--border-strong)" strokeWidth="1.5" />
      </svg>
      <div className="orb__chip">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M12 6v12M6 12h12" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" />
        </svg>
      </div>
    </div>
  );
}
