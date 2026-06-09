import type { Mode } from "../api/types";
import { MODES } from "../api/types";

interface ToneCardProps {
  mode: Mode;
  onModeChange: (mode: Mode) => void;
}

/** Desktop right-rail tone selector: one row per mode (label + hint + radio).
 * Bound to the same `mode` state as the mobile chip row. */
export function ToneCard({ mode, onModeChange }: ToneCardProps) {
  const current = MODES.find((m) => m.value === mode);
  return (
    <div className="tone-card">
      <div className="tone-card__head">
        <div>
          <div className="card__title">Tone</div>
          <div className="card__subtitle">Shapes every draft</div>
        </div>
        <span className="tone-card__current">{current?.label ?? mode}</span>
      </div>

      <div className="tone-card__rows" role="radiogroup" aria-label="Tone">
        {MODES.map((m) => {
          const active = m.value === mode;
          return (
            <button
              key={m.value}
              type="button"
              role="radio"
              aria-checked={active}
              className={"tone-row" + (active ? " tone-row--active" : "")}
              onClick={() => onModeChange(m.value)}
            >
              <span className="tone-row__text">
                <span className="tone-row__label">{m.label}</span>
                <span className="tone-row__hint">{m.hint}</span>
              </span>
              <span className="tone-row__radio" aria-hidden="true" />
            </button>
          );
        })}
      </div>
    </div>
  );
}
