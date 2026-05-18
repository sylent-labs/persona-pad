import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { Sidebar } from "./Sidebar";
import { QUICK_ACTIONS } from "../quickActions";

const personas = [
  { id: "van_keith", display_name: "Van Keith" },
  { id: "other", display_name: "Other Persona" },
];

describe("Sidebar", () => {
  it("calls onPersonaChange when a persona is clicked", async () => {
    const onPersonaChange = vi.fn();
    const user = userEvent.setup();
    render(
      <Sidebar
        personas={personas}
        personaId="van_keith"
        onPersonaChange={onPersonaChange}
        onQuickAction={vi.fn()}
        quickActionsDisabled={false}
      />,
    );

    await user.click(screen.getByRole("button", { name: /other persona/i }));

    expect(onPersonaChange).toHaveBeenCalledWith("other");
  });

  it("fires onQuickAction with the preset message when a quick action is clicked", async () => {
    const onQuickAction = vi.fn();
    const user = userEvent.setup();
    render(
      <Sidebar
        personas={personas}
        personaId="van_keith"
        onPersonaChange={vi.fn()}
        onQuickAction={onQuickAction}
        quickActionsDisabled={false}
      />,
    );

    const action = QUICK_ACTIONS[0]!;
    await user.click(screen.getByRole("button", { name: action.label }));

    expect(onQuickAction).toHaveBeenCalledWith(action.message);
  });

  it("disables every quick action button when quickActionsDisabled is true", () => {
    render(
      <Sidebar
        personas={personas}
        personaId="van_keith"
        onPersonaChange={vi.fn()}
        onQuickAction={vi.fn()}
        quickActionsDisabled
      />,
    );

    for (const action of QUICK_ACTIONS) {
      expect(screen.getByRole("button", { name: action.label })).toBeDisabled();
    }
  });
});
