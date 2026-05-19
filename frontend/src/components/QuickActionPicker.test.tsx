import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { QuickActionPicker } from "./QuickActionPicker";
import { QUICK_ACTIONS } from "../quickActions";

describe("QuickActionPicker", () => {
  it("calls onQuickAction with the preset message when an action is picked", async () => {
    const onQuickAction = vi.fn();
    const user = userEvent.setup();
    render(<QuickActionPicker onQuickAction={onQuickAction} disabled={false} />);

    const action = QUICK_ACTIONS[0]!;
    await user.selectOptions(
      screen.getByRole("combobox", { name: /quick action/i }),
      action.id,
    );

    expect(onQuickAction).toHaveBeenCalledWith(action.message, action.mode);
  });

  it("passes the email mode when the Email template action is picked", async () => {
    const onQuickAction = vi.fn();
    const user = userEvent.setup();
    render(<QuickActionPicker onQuickAction={onQuickAction} disabled={false} />);

    const emailAction = QUICK_ACTIONS.find((a) => a.id === "email-template");
    expect(emailAction).toBeDefined();
    await user.selectOptions(
      screen.getByRole("combobox", { name: /quick action/i }),
      emailAction!.id,
    );

    expect(onQuickAction).toHaveBeenCalledWith(emailAction!.message, "email");
  });

  it("resets back to the placeholder after a selection so it can fire again", async () => {
    const onQuickAction = vi.fn();
    const user = userEvent.setup();
    render(<QuickActionPicker onQuickAction={onQuickAction} disabled={false} />);

    const select = screen.getByRole("combobox", {
      name: /quick action/i,
    }) as HTMLSelectElement;

    const action = QUICK_ACTIONS[1]!;
    await user.selectOptions(select, action.id);

    expect(select.value).toBe("");
  });

  it("is disabled when the parent says disabled", () => {
    render(<QuickActionPicker onQuickAction={vi.fn()} disabled />);
    expect(screen.getByRole("combobox", { name: /quick action/i })).toBeDisabled();
  });
});
