import type { Mode } from "./api/types";

/** A turn typed by the user, rendered as the accent bubble on the right. */
export interface UserMessage {
  id: string;
  role: "user";
  text: string;
}

/**
 * One persona response, rendered as a block: header + OPTION 1 (draft),
 * OPTION 2 (alternate), and the style-notes chips. `mode` is captured at
 * generation time so the block's pill reflects how the draft was produced,
 * not the currently selected mode.
 */
export interface PersonaMessage {
  id: string;
  role: "persona";
  draft: string;
  alternate: string;
  styleNotes: string[];
  mode: Mode;
}

export type ChatMessage = UserMessage | PersonaMessage;
