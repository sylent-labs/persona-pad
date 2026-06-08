import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { Sidebar } from "./Sidebar";
import { QUICK_ACTIONS } from "../quickActions";

const personas = [
  { id: "van_keith", display_name: "Van Keith", default_mode: "raw" as const },
  { id: "other", display_name: "Other Persona", default_mode: "raw" as const },
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

    expect(onQuickAction).toHaveBeenCalledWith(action.message, action.mode);
  });

  it("passes the email mode for the Email template quick action", async () => {
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

    const emailAction = QUICK_ACTIONS.find((a) => a.id === "email-template");
    expect(emailAction).toBeDefined();
    await user.click(screen.getByRole("button", { name: emailAction!.label }));

    expect(onQuickAction).toHaveBeenCalledWith(emailAction!.message, "email");
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
