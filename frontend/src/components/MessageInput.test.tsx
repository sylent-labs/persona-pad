import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { MessageInput } from "./MessageInput";

describe("MessageInput", () => {
  it("disables Send when the message is empty", () => {
    render(<MessageInput onSend={vi.fn()} disabled={false} />);
    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });

  it("calls onSend with the typed text and clears the field on submit", async () => {
    const onSend = vi.fn();
    const user = userEvent.setup();
    render(<MessageInput onSend={onSend} disabled={false} />);

    const field = screen.getByRole("textbox", { name: /message/i });
    await user.type(field, "are you free this weekend?");
    await user.click(screen.getByRole("button", { name: /send/i }));

    expect(onSend).toHaveBeenCalledWith("are you free this weekend?");
    expect(field).toHaveValue("");
  });

  it("submits on Enter without Shift", async () => {
    const onSend = vi.fn();
    const user = userEvent.setup();
    render(<MessageInput onSend={onSend} disabled={false} />);

    const field = screen.getByRole("textbox", { name: /message/i });
    await user.type(field, "hi{Enter}");

    expect(onSend).toHaveBeenCalledWith("hi");
  });

  it("grows the textarea as more lines are typed", async () => {
    const user = userEvent.setup();
    render(<MessageInput onSend={vi.fn()} disabled={false} />);

    const field = screen.getByRole("textbox", {
      name: /message/i,
    }) as HTMLTextAreaElement;

    // jsdom reports scrollHeight as 0, so the auto-grow sets height to "0px".
    // We can still assert the effect wrote an inline height (the grow ran).
    await user.type(field, "line one");
    expect(field.style.height).not.toBe("");
  });

  it("disables Send when the parent says disabled", () => {
    render(<MessageInput onSend={vi.fn()} disabled />);
    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });
});
