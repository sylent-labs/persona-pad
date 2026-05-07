import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ChatBox } from "./ChatBox";

describe("ChatBox", () => {
  it("Generate is disabled when question is empty", () => {
    render(<ChatBox onSubmit={vi.fn()} loading={false} />);
    expect(screen.getByRole("button", { name: /generate/i })).toBeDisabled();
  });

  it("submits the typed question, context, and selected mode", async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<ChatBox onSubmit={onSubmit} loading={false} />);

    await user.type(
      screen.getByRole("textbox", { name: /^question$/i }),
      "Why should we hire you?",
    );
    await user.type(
      screen.getByRole("textbox", { name: /context/i }),
      "recruiter",
    );
    await user.selectOptions(screen.getByRole("combobox"), "raw_vk");
    await user.click(screen.getByRole("button", { name: /generate/i }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmit).toHaveBeenCalledWith({
      question: "Why should we hire you?",
      context: "recruiter",
      mode: "raw_vk",
    });
  });

  it("shows the drafting label and stays disabled while loading", () => {
    render(<ChatBox onSubmit={vi.fn()} loading={true} />);
    expect(screen.getByRole("button", { name: /drafting/i })).toBeDisabled();
  });
});
