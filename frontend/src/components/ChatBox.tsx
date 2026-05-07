import { useState } from "react";

import type { GenerateRequest, Mode, Persona } from "../api/types";
import { MODES } from "../api/types";

interface ChatBoxProps {
  personas: Persona[];
  personaId: string;
  onPersonaChange: (personaId: string) => void;
  onSubmit: (req: GenerateRequest) => void;
  loading: boolean;
}

export function ChatBox({
  personas,
  personaId,
  onPersonaChange,
  onSubmit,
  loading,
}: ChatBoxProps) {
  const [question, setQuestion] = useState("");
  const [context, setContext] = useState("");
  const [mode, setMode] = useState<Mode>("professional_vk");

  const trimmed = question.trim();
  const personasReady = personas.length > 0 && personaId.length > 0;
  const disabled = loading || trimmed.length === 0 || !personasReady;

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (disabled) return;
    onSubmit({
      persona_id: personaId,
      question: trimmed,
      context: context.trim(),
      mode,
    });
  }

  return (
    <form className="chatbox" onSubmit={handleSubmit}>
      <label className="field">
        <span className="field-label">Persona</span>
        <select
          name="persona"
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
      </label>

      <label className="field">
        <span className="field-label">Question</span>
        <textarea
          name="question"
          rows={4}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder='e.g. "Why should we hire you?"'
        />
      </label>

      <label className="field">
        <span className="field-label">Context (optional)</span>
        <textarea
          name="context"
          rows={2}
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="e.g. recruiter screening for a senior backend role"
        />
      </label>

      <label className="field">
        <span className="field-label">Mode</span>
        <select
          name="mode"
          value={mode}
          onChange={(e) => setMode(e.target.value as Mode)}
        >
          {MODES.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label}
            </option>
          ))}
        </select>
        <span className="field-hint">
          {MODES.find((m) => m.value === mode)?.hint}
        </span>
      </label>

      <button type="submit" disabled={disabled}>
        {loading ? "Drafting..." : "Generate"}
      </button>
    </form>
  );
}
