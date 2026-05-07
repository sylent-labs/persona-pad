import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { MessageInput } from "./MessageInput";

describe("MessageInput", () => {
  it("disables Send when the message is empty", () => {
    render(
      <MessageInput
        onSend={vi.fn()}
        mode="raw"
        onModeChange={vi.fn()}
        disabled={false}
      />,
    );
    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });

  it("calls onSend with the typed text and clears the field on submit", async () => {
    const onSend = vi.fn();
    const user = userEvent.setup();
    render(
      <MessageInput
        onSend={onSend}
        mode="raw"
        onModeChange={vi.fn()}
        disabled={false}
      />,
    );

    const field = screen.getByRole("textbox", { name: /message/i });
    await user.type(field, "are you free this weekend?");
    await user.click(screen.getByRole("button", { name: /send/i }));

    expect(onSend).toHaveBeenCalledWith("are you free this weekend?");
    expect(field).toHaveValue("");
  });

  it("submits on Enter without Shift", async () => {
    const onSend = vi.fn();
    const user = userEvent.setup();
    render(
      <MessageInput
        onSend={onSend}
        mode="raw"
        onModeChange={vi.fn()}
        disabled={false}
      />,
    );

    const field = screen.getByRole("textbox", { name: /message/i });
    await user.type(field, "hi{Enter}");

    expect(onSend).toHaveBeenCalledWith("hi");
  });

  it("calls onModeChange when a mode chip is tapped", async () => {
    const onModeChange = vi.fn();
    const user = userEvent.setup();
    render(
      <MessageInput
        onSend={vi.fn()}
        mode="raw"
        onModeChange={onModeChange}
        disabled={false}
      />,
    );

    await user.click(screen.getByRole("radio", { name: /professional/i }));

    expect(onModeChange).toHaveBeenCalledWith("professional");
  });

  it("disables Send when the parent says disabled", () => {
    render(
      <MessageInput
        onSend={vi.fn()}
        mode="raw"
        onModeChange={vi.fn()}
        disabled
      />,
    );
    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });
});
