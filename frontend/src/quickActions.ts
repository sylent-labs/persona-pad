export interface QuickAction {
  id: string;
  label: string;
  message: string;
}

export const QUICK_ACTIONS: ReadonlyArray<QuickAction> = [
  {
    id: "tell-me-about-yourself",
    label: "Tell me about yourself",
    message:
      "Tell me about yourself. Keep it to the relevant highlights — skip the full history.",
  },
  {
    id: "why-leaving",
    label: "Why are you leaving",
    message: "Why are you leaving your current role?",
  },
  {
    id: "what-looking-for",
    label: "What are you looking for",
    message: "What are you looking for in your next role?",
  },
  {
    id: "projects-leading",
    label: "What projects are you leading",
    message: "What projects are you currently leading?",
  },
  {
    id: "salary-expectations",
    label: "Salary expectations",
    message: "What are your salary expectations?",
  },
];
