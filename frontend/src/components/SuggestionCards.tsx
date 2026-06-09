import type { ReactNode } from "react";

import { QUICK_ACTIONS, type QuickAction } from "../quickActions";

interface SuggestionCardsProps {
  onQuickAction: (action: QuickAction) => void;
  disabled: boolean;
}

interface SuggestionCard {
  actionId: string;
  category: string;
  prompt: string;
  icon: ReactNode;
}

/**
 * The four hero cards map to existing quick actions (so a click fires the same
 * generation path). `prompt` is the card's display copy; the message that gets
 * sent is the mapped action's `message`.
 */
const CARDS: ReadonlyArray<SuggestionCard> = [
  {
    actionId: "tell-me-about-yourself",
    category: "About me",
    prompt: "Tell me about yourself and what you do.",
    icon: <UserIcon />,
  },
  {
    actionId: "why-leaving",
    category: "Career",
    prompt: "Why are you leaving your current role?",
    icon: <PathIcon />,
  },
  {
    actionId: "projects-leading",
    category: "Projects",
    prompt: "What projects are you leading right now?",
    icon: <LayersIcon />,
  },
  {
    actionId: "salary-expectations",
    category: "Comp · Email",
    prompt: "What are your salary expectations?",
    icon: <CompIcon />,
  },
];

export function SuggestionCards({ onQuickAction, disabled }: SuggestionCardsProps) {
  return (
    <div className="suggestions">
      {CARDS.map((card) => {
        const action = QUICK_ACTIONS.find((a) => a.id === card.actionId);
        if (!action) return null;
        return (
          <button
            key={card.actionId}
            type="button"
            className="suggestion"
            disabled={disabled}
            onClick={() => onQuickAction(action)}
          >
            <span className="suggestion__icon" aria-hidden="true">
              {card.icon}
            </span>
            <span className="suggestion__body">
              <span className="suggestion__category">{card.category}</span>
              <span className="suggestion__prompt">{card.prompt}</span>
            </span>
          </button>
        );
      })}
    </div>
  );
}

function UserIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="8" r="4" />
      <path d="M5 20c0-3.5 3-6 7-6s7 2.5 7 6" />
    </svg>
  );
}

function PathIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M5 19c4 0 4-7 8-7s4-7 6-7" />
      <path d="M16 5h3v3" />
    </svg>
  );
}

function LayersIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 3l9 5-9 5-9-5 9-5z" />
      <path d="M3 13l9 5 9-5" />
    </svg>
  );
}

function CompIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v10M9.5 9.5h4a1.5 1.5 0 0 1 0 3h-3a1.5 1.5 0 0 0 0 3h4.5" />
    </svg>
  );
}
