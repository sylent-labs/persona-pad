import type { QuickAction } from "../quickActions";
import { BrandMark } from "./BrandMark";
import { QuickActionGroups } from "./QuickActionGroups";

interface SidebarProps {
  onQuickAction: (action: QuickAction) => void;
  activeActionId: string | null;
  quickActionsDisabled: boolean;
}

/**
 * Desktop sidebar (decision A2.3): brand mark + the two Quick Action groups
 * only. No persona switcher, history, search, or new-chat — the app is
 * single-persona.
 */
export function Sidebar({
  onQuickAction,
  activeActionId,
  quickActionsDisabled,
}: SidebarProps) {
  return (
    <aside className="sidebar" aria-label="Van Keith Intelligence">
      <div className="sidebar__brand">
        <BrandMark />
        <span className="sidebar__brand-text">
          <span className="sidebar__brand-name">Van Keith</span>
          <span className="sidebar__brand-tag">Intelligence</span>
        </span>
      </div>

      <div className="sidebar__actions">
        <QuickActionGroups
          onQuickAction={onQuickAction}
          activeActionId={activeActionId}
          disabled={quickActionsDisabled}
        />
      </div>
    </aside>
  );
}
