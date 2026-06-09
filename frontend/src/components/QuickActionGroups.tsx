import type { QuickAction } from "../quickActions";
import {
  QUICK_ACTIONS,
  QUICK_ACTION_GROUP_LABELS,
  QUICK_ACTION_GROUP_ORDER,
} from "../quickActions";

interface QuickActionGroupsProps {
  onQuickAction: (action: QuickAction) => void;
  activeActionId: string | null;
  disabled: boolean;
}

/**
 * The grouped Quick Action list (Chat + Email). Shared by the desktop sidebar
 * and the mobile drawer so the labels, order, and active-item highlight live in
 * one place.
 */
export function QuickActionGroups({
  onQuickAction,
  activeActionId,
  disabled,
}: QuickActionGroupsProps) {
  return (
    <>
      {QUICK_ACTION_GROUP_ORDER.map((group) => {
        const groupActions = QUICK_ACTIONS.filter((a) => a.group === group);
        if (groupActions.length === 0) return null;
        const groupLabel = QUICK_ACTION_GROUP_LABELS[group];
        return (
          <div key={group} className="quick-group">
            <div className="quick-group__label">{groupLabel}</div>
            <nav className="quick-group__list" aria-label={groupLabel}>
              {groupActions.map((action) => {
                const active = action.id === activeActionId;
                return (
                  <button
                    key={action.id}
                    type="button"
                    className={
                      "quick-item" + (active ? " quick-item--active" : "")
                    }
                    aria-current={active ? "true" : undefined}
                    disabled={disabled}
                    onClick={() => onQuickAction(action)}
                  >
                    {action.label}
                  </button>
                );
              })}
            </nav>
          </div>
        );
      })}
    </>
  );
}
