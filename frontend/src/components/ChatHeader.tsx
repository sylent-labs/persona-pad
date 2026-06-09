import type { QuickAction } from "../quickActions";
import { BrandMark } from "./BrandMark";
import { QuickActionGroups } from "./QuickActionGroups";

interface ChatHeaderProps {
  drawerOpen: boolean;
  onToggleDrawer: () => void;
  onQuickAction: (action: QuickAction) => void;
  activeActionId: string | null;
  quickActionsDisabled: boolean;
}

/**
 * Mobile-only top bar (desktop has no top bar — decision A2 layout). Left: a
 * hamburger that opens the Quick Actions drawer. Center: the "VK Van Keith"
 * badge (no chevron, no switcher).
 */
export function ChatHeader({
  drawerOpen,
  onToggleDrawer,
  onQuickAction,
  activeActionId,
  quickActionsDisabled,
}: ChatHeaderProps) {
  return (
    <header className="mobile-header">
      <button
        type="button"
        className="mobile-header__menu"
        aria-label="Quick actions"
        aria-expanded={drawerOpen}
        onClick={onToggleDrawer}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
          <path d="M4 7h16M4 12h16M4 17h16" />
        </svg>
      </button>

      <div className="mobile-header__badge">
        <span className="mobile-header__avatar" aria-hidden="true">VK</span>
        <span className="mobile-header__name">Van Keith</span>
      </div>

      {drawerOpen ? (
        <div className="drawer">
          <button
            type="button"
            className="drawer__scrim"
            aria-label="Close quick actions"
            onClick={onToggleDrawer}
          />
          <div className="drawer__panel" role="dialog" aria-label="Quick actions">
            <div className="drawer__brand">
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
          </div>
        </div>
      ) : null}
    </header>
  );
}
