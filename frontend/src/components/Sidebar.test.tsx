import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { Sidebar } from "./Sidebar";
import { QUICK_ACTIONS } from "../quickActions";

describe("Sidebar", () => {
  it("renders the VKI brand", () => {
    render(
      <Sidebar
        onQuickAction={vi.fn()}
        activeActionId={null}
        quickActionsDisabled={false}
      />,
    );
    expect(screen.getByText("Van Keith")).toBeInTheDocument();
    expect(screen.getByText("Intelligence")).toBeInTheDocument();
  });

  it("renders every quick action grouped into Chat and Email", () => {
    render(
      <Sidebar
        onQuickAction={vi.fn()}
        activeActionId={null}
        quickActionsDisabled={false}
      />,
    );
    expect(screen.getByText("Quick Actions — Chat")).toBeInTheDocument();
    expect(screen.getByText("Quick Actions — Email")).toBeInTheDocument();
    for (const action of QUICK_ACTIONS) {
      expect(
        screen.getByRole("button", { name: action.label }),
      ).toBeInTheDocument();
    }
  });

  it("fires onQuickAction with the full action when one is clicked", async () => {
    const onQuickAction = vi.fn();
    const user = userEvent.setup();
    render(
      <Sidebar
        onQuickAction={onQuickAction}
        activeActionId={null}
        quickActionsDisabled={false}
      />,
    );

    const action = QUICK_ACTIONS[0]!;
    await user.click(screen.getByRole("button", { name: action.label }));

    expect(onQuickAction).toHaveBeenCalledWith(action);
  });

  it("marks the active action's button as current", () => {
    const action = QUICK_ACTIONS.find((a) => a.id === "why-leaving")!;
    render(
      <Sidebar
        onQuickAction={vi.fn()}
        activeActionId={action.id}
        quickActionsDisabled={false}
      />,
    );

    const button = screen.getByRole("button", { name: action.label });
    expect(button).toHaveAttribute("aria-current", "true");
  });

  it("disables every quick action button when quickActionsDisabled is true", () => {
    render(
      <Sidebar
        onQuickAction={vi.fn()}
        activeActionId={null}
        quickActionsDisabled
      />,
    );

    for (const action of QUICK_ACTIONS) {
      expect(screen.getByRole("button", { name: action.label })).toBeDisabled();
    }
  });
});
