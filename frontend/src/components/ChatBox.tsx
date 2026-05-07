import { useState } from "react";

import type { GenerateRequest, Mode } from "../api/types";
import { MODES } from "../api/types";

interface ChatBoxProps {
  onSubmit: (req: GenerateRequest) => void;
  loading: boolean;
}

export function ChatBox({ onSubmit, loading }: ChatBoxProps) {
  const [question, setQuestion] = useState("");
  const [context, setContext] = useState("");
  const [mode, setMode] = useState<Mode>("professional_vk");

  const trimmed = question.trim();
  const disabled = loading || trimmed.length === 0;

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (disabled) return;
    onSubmit({ question: trimmed, context: context.trim(), mode });
  }

  return (
    <form className="chatbox" onSubmit={handleSubmit}>
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
