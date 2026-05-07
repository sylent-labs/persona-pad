import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import type { Persona } from "../api/types";
import { ChatBox } from "./ChatBox";

const PERSONAS: Persona[] = [
  { id: "van_keith", display_name: "Van Keith" },
  { id: "mike_ross", display_name: "Mike Ross" },
];

function renderChatBox(
  overrides: Partial<{
    personas: Persona[];
    personaId: string;
    onPersonaChange: (id: string) => void;
    onSubmit: (req: unknown) => void;
    loading: boolean;
  }> = {},
) {
  const props = {
    personas: PERSONAS,
    personaId: PERSONAS[0]!.id,
    onPersonaChange: vi.fn(),
    onSubmit: vi.fn(),
    loading: false,
    ...overrides,
  };
  render(<ChatBox {...props} />);
  return props;
}

describe("ChatBox", () => {
  it("Generate is disabled when question is empty", () => {
    renderChatBox();
    expect(screen.getByRole("button", { name: /generate/i })).toBeDisabled();
  });

  it("Generate is disabled when no personas have loaded", () => {
    renderChatBox({ personas: [], personaId: "" });
    expect(screen.getByRole("button", { name: /generate/i })).toBeDisabled();
  });

  it("submits the persona, question, context, and selected mode", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    renderChatBox({ onSubmit });

    await user.type(
      screen.getByRole("textbox", { name: /^question$/i }),
      "Why should we hire you?",
    );
    await user.type(
      screen.getByRole("textbox", { name: /context/i }),
      "recruiter",
    );
    await user.selectOptions(screen.getByRole("combobox", { name: /mode/i }), "raw_vk");
    await user.click(screen.getByRole("button", { name: /generate/i }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmit).toHaveBeenCalledWith({
      persona_id: "van_keith",
      question: "Why should we hire you?",
      context: "recruiter",
      mode: "raw_vk",
    });
  });

  it("calls onPersonaChange when a different persona is selected", async () => {
    const onPersonaChange = vi.fn();
    const user = userEvent.setup();
    renderChatBox({ onPersonaChange });

    await user.selectOptions(
      screen.getByRole("combobox", { name: /persona/i }),
      "mike_ross",
    );

    expect(onPersonaChange).toHaveBeenCalledWith("mike_ross");
  });

  it("shows the drafting label and stays disabled while loading", () => {
    renderChatBox({ loading: true });
    expect(screen.getByRole("button", { name: /drafting/i })).toBeDisabled();
  });
});
