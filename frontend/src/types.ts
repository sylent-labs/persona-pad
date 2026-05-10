export type ChatRole = "user" | "persona";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  text: string;
  label?: string;
}
