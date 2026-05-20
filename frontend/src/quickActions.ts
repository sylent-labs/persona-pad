import type { Mode } from "./api/types";

export type QuickActionGroup = "chat" | "email";

export interface QuickAction {
  id: string;
  label: string;
  message: string;
  mode?: Mode;
  group: QuickActionGroup;
}

export const QUICK_ACTION_GROUP_LABELS: Record<QuickActionGroup, string> = {
  chat: "Quick Actions — Chat",
  email: "Quick Actions — Email",
};

export const QUICK_ACTION_GROUP_ORDER: ReadonlyArray<QuickActionGroup> = [
  "chat",
  "email",
];

export const QUICK_ACTIONS: ReadonlyArray<QuickAction> = [
  {
    id: "tell-me-about-yourself",
    label: "Tell me about yourself",
    message:
      "Tell me about yourself. Keep it to the relevant highlights — skip the full history.",
    group: "chat",
  },
  {
    id: "why-leaving",
    label: "Why are you leaving",
    message: "Why are you leaving your current role?",
    group: "chat",
  },
  {
    id: "what-looking-for",
    label: "What are you looking for",
    message: "What are you looking for in your next role?",
    group: "chat",
  },
  {
    id: "projects-leading",
    label: "What projects are you leading",
    message: "What projects are you currently leading?",
    group: "chat",
  },
  {
    id: "salary-expectations",
    label: "Salary expectations",
    message: "What are your salary expectations?",
    group: "chat",
  },
  {
    id: "linkedin",
    label: "LinkedIn",
    message: "What's your LinkedIn?",
    group: "chat",
  },
  {
    id: "github",
    label: "GitHub",
    message: "What's your GitHub?",
    group: "chat",
  },
  {
    id: "email-availability",
    label: "Email availability",
    message: "Availability",
    mode: "email",
    group: "email",
  },
  {
    id: "email-template",
    label: "Email template",
    message: "Template",
    mode: "email",
    group: "email",
  },
];
