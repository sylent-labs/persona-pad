import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ResponseCard } from "./ResponseCard";

function stubClipboard() {
  const writeText = vi.fn().mockResolvedValue(undefined);
  Object.defineProperty(navigator, "clipboard", {
    value: { writeText },
    configurable: true,
    writable: true,
  });
  return writeText;
}

describe("ResponseCard", () => {
  it("renders the title and body", () => {
    render(<ResponseCard title="Draft" body="hello world" />);
    expect(screen.getByRole("heading", { name: /draft/i })).toBeInTheDocument();
    expect(screen.getByText("hello world")).toBeInTheDocument();
  });

  it("copies the body to the clipboard when Copy is clicked", async () => {
    const user = userEvent.setup();
    const writeText = stubClipboard();
    render(<ResponseCard title="Draft" body="copy me please" />);

    await user.click(screen.getByRole("button", { name: /copy draft/i }));

    expect(writeText).toHaveBeenCalledWith("copy me please");
    expect(await screen.findByText(/copied!/i)).toBeInTheDocument();
  });
});
