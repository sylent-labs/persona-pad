export type Mode = "raw_vk" | "professional_vk" | "short_vk";

export interface GenerateRequest {
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
    value: "professional_vk",
    label: "Professional VK",
    hint: "Direct but cleaned up — recruiter, client, interview.",
  },
  {
    value: "raw_vk",
    label: "Raw VK",
    hint: "Conversational rhythm — DMs, slack, casual replies.",
  },
  {
    value: "short_vk",
    label: "Short VK",
    hint: "Five sentences or fewer — quick replies and texts.",
  },
];
