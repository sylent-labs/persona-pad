import type { Mode } from "../api/types";
import { MODES } from "../api/types";

interface ModeChipsProps {
  mode: Mode;
  onModeChange: (mode: Mode) => void;
}

/** Mobile mode selector — a horizontal chip row above the composer. The desktop
 * equivalent is the Tone card in the right rail. Both bind the same `mode`. */
export function ModeChips({ mode, onModeChange }: ModeChipsProps) {
  return (
    <div className="mode-chips" role="radiogroup" aria-label="Reply mode">
      {MODES.map((m) => (
        <button
          key={m.value}
          type="button"
          role="radio"
          aria-checked={m.value === mode}
          className={"mode-chip" + (m.value === mode ? " mode-chip--active" : "")}
          onClick={() => onModeChange(m.value)}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}
