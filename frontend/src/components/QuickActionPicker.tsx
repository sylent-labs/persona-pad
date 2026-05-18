import { QUICK_ACTIONS } from "../quickActions";

interface QuickActionPickerProps {
  onQuickAction: (message: string) => void;
  disabled: boolean;
}

export function QuickActionPicker({ onQuickAction, disabled }: QuickActionPickerProps) {
  function handleChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const id = event.target.value;
    if (!id) return;
    const action = QUICK_ACTIONS.find((a) => a.id === id);
    event.target.value = "";
    if (action) onQuickAction(action.message);
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
      {QUICK_ACTIONS.map((a) => (
        <option key={a.id} value={a.id}>
          {a.label}
        </option>
      ))}
    </select>
  );
}
