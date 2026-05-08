import type { Persona } from "../api/types";

interface SidebarProps {
  personas: Persona[];
  personaId: string;
  onPersonaChange: (id: string) => void;
}

function initials(displayName: string): string {
  const parts = displayName.split(" ").filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0]!.charAt(0).toUpperCase();
  return (
    parts[0]!.charAt(0) + parts[parts.length - 1]!.charAt(0)
  ).toUpperCase();
}

export function Sidebar({ personas, personaId, onPersonaChange }: SidebarProps) {
  return (
    <aside className="sidebar" aria-label="Personas">
      <div className="sidebar__brand">
        <div className="sidebar__brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a4 4 0 0 1-4 4H8l-5 4V6a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" />
          </svg>
        </div>
        <div className="sidebar__brand-text">
          <span className="sidebar__brand-name">PersonaPad</span>
          <span className="sidebar__brand-tag">Private digital personas</span>
        </div>
      </div>

      <div className="sidebar__section-label">Personas</div>

      <nav className="sidebar__list" aria-label="Choose persona">
        {personas.length === 0 ? (
          <div className="sidebar__empty">Loading personas...</div>
        ) : (
          personas.map((p) => {
            const active = p.id === personaId;
            return (
              <button
                key={p.id}
                type="button"
                className={
                  "sidebar__item" + (active ? " sidebar__item--active" : "")
                }
                aria-current={active ? "true" : undefined}
                onClick={() => onPersonaChange(p.id)}
              >
                <span className="sidebar__avatar" aria-hidden="true">
                  {initials(p.display_name)}
                </span>
                <span className="sidebar__item-name">{p.display_name}</span>
              </button>
            );
          })
        )}
      </nav>

      <div className="sidebar__footer">
        <span>Replies are drafts in their voice.</span>
        <span>Always your call to send.</span>
      </div>
    </aside>
  );
}
