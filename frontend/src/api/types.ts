export type Mode = "raw" | "professional" | "short";

export interface Persona {
  id: string;
  display_name: string;
}

export interface GenerateRequest {
  persona_id: string;
  question: string;
  context: string;
  mode: Mode;
}

export interface GenerateResponse {
  draft: string;
  alternate: string;
  style_notes: string[];
}

export const MODES: ReadonlyArray<{
  value: Mode;
  label: string;
  hint: string;
}> = [
  {
    value: "professional",
    label: "Professional",
    hint: "Direct but cleaned up for recruiter, client, interview.",
  },
  {
    value: "raw",
    label: "Raw",
    hint: "Conversational rhythm for DMs, slack, casual replies.",
  },
  {
    value: "short",
    label: "Short",
    hint: "Five sentences or fewer for quick replies and texts.",
  },
];
