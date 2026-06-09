import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { SuggestionCards } from "./SuggestionCards";
import { QUICK_ACTIONS } from "../quickActions";

describe("SuggestionCards", () => {
  it("renders the four hero prompts", () => {
    render(<SuggestionCards onQuickAction={vi.fn()} disabled={false} />);
    expect(
      screen.getByText("Tell me about yourself and what you do."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Why are you leaving your current role?"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("What projects are you leading right now?"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("What are your salary expectations?"),
    ).toBeInTheDocument();
  });

  it("fires the mapped quick action when a card is clicked", async () => {
    const onQuickAction = vi.fn();
    const user = userEvent.setup();
    render(<SuggestionCards onQuickAction={onQuickAction} disabled={false} />);

    await user.click(
      screen.getByText("Why are you leaving your current role?"),
    );

    const expected = QUICK_ACTIONS.find((a) => a.id === "why-leaving");
    expect(onQuickAction).toHaveBeenCalledWith(expected);
  });

  it("disables the cards when disabled", () => {
    render(<SuggestionCards onQuickAction={vi.fn()} disabled />);
    for (const card of screen.getAllByRole("button")) {
      expect(card).toBeDisabled();
    }
  });
});
