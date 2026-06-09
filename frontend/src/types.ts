import type { Mode } from "./api/types";

/** A turn typed by the user, rendered as the accent bubble on the right. */
export interface UserMessage {
  id: string;
  role: "user";
  text: string;
}

/**
 * One persona response, rendered as a block: header + OPTION 1 (draft) and
 * OPTION 2 (alternate). `mode` is captured at generation time so the block's
 * pill reflects how the draft was produced, not the currently selected mode.
 */
export interface PersonaMessage {
  id: string;
  role: "persona";
  draft: string;
  alternate: string;
  /** Strategic reply guidance, surfaced in the right-rail Guide card rather than
   * inline. Arrives with the draft from the same /api/generate call. */
  guide: string[];
  mode: Mode;
}

export type ChatMessage = UserMessage | PersonaMessage;
