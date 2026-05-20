import type { Mode } from "../api/types";
import {
  QUICK_ACTIONS,
  QUICK_ACTION_GROUP_LABELS,
  QUICK_ACTION_GROUP_ORDER,
} from "../quickActions";

interface QuickActionPickerProps {
  onQuickAction: (message: string, mode?: Mode) => void;
  disabled: boolean;
}

export function QuickActionPicker({ onQuickAction, disabled }: QuickActionPickerProps) {
  function handleChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const id = event.target.value;
    if (!id) return;
    const action = QUICK_ACTIONS.find((a) => a.id === id);
    event.target.value = "";
    if (action) onQuickAction(action.message, action.mode);
  }

  return (
    <select
      className="chat-header__select chat-header__select--quick"
      aria-label="Quick action"
      value=""
      onChange={handleChange}
      disabled={disabled}
    >
      <option value="" disabled>
        Quick action…
      </option>
      {QUICK_ACTION_GROUP_ORDER.map((group) => {
        const groupActions = QUICK_ACTIONS.filter((a) => a.group === group);
        if (groupActions.length === 0) return null;
        return (
          <optgroup key={group} label={QUICK_ACTION_GROUP_LABELS[group]}>
            {groupActions.map((a) => (
              <option key={a.id} value={a.id}>
                {a.label}
              </option>
            ))}
          </optgroup>
        );
      })}
    </select>
  );
}
