import type { Persona } from "../api/types";

interface ChatHeaderProps {
  personas: Persona[];
  personaId: string;
  onPersonaChange: (id: string) => void;
}

function initials(displayName: string): string {
  const parts = displayName.split(" ").filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0]!.charAt(0).toUpperCase();
  return (parts[0]!.charAt(0) + parts[parts.length - 1]!.charAt(0)).toUpperCase();
}

export function ChatHeader({ personas, personaId, onPersonaChange }: ChatHeaderProps) {
  const current = personas.find((p) => p.id === personaId);
  const displayName = current?.display_name ?? "Loading...";

  return (
    <header className="chat-header">
      <div className="chat-header__avatar" aria-hidden="true">
        {current ? initials(displayName) : "·"}
      </div>
      <div className="chat-header__title">
        <div className="chat-header__name-row">
          {/* Mobile: dropdown to switch personas. Desktop: sidebar handles it. */}
          <select
            className="chat-header__select"
            aria-label="Persona"
            value={personaId}
            onChange={(e) => onPersonaChange(e.target.value)}
            disabled={personas.length === 0}
          >
            {personas.length === 0 ? (
              <option value="">Loading personas...</option>
            ) : (
              personas.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.display_name}
                </option>
              ))
            )}
          </select>
          <span className="chat-header__name">{displayName}</span>
        </div>
        <span className="chat-header__subtitle">
          Drafting replies in their voice
        </span>
      </div>
    </header>
  );
}
