import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { Bubble, TypingBubble } from "./Bubble";

describe("Bubble", () => {
  it("renders user bubble text and applies the user role class", () => {
    const { container } = render(<Bubble role="user" text="hi there" />);
    expect(screen.getByText("hi there")).toBeInTheDocument();
    const bubble = container.querySelector(".bubble");
    expect(bubble?.className).toContain("bubble--user");
  });

  it("renders persona bubble text and applies the persona role class", () => {
    const { container } = render(<Bubble role="persona" text="yeah probably" />);
    expect(screen.getByText("yeah probably")).toBeInTheDocument();
    const bubble = container.querySelector(".bubble");
    expect(bubble?.className).toContain("bubble--persona");
  });

  it("hides the copy button when showCopy is false (user bubble)", () => {
    render(<Bubble role="user" text="my own words" showCopy={false} />);
    expect(
      screen.queryByRole("button", { name: /copy/i }),
    ).not.toBeInTheDocument();
  });
});

describe("Bubble copy button", () => {
  function installClipboardMock() {
    const writeText = vi.fn().mockResolvedValue(undefined);
    // userEvent.setup() v14 installs its own clipboard mock, so override it
    // after setup runs.
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText },
    });
    return writeText;
  }

  it("copies the bubble text", async () => {
    const user = userEvent.setup();
    const writeText = installClipboardMock();
    render(<Bubble role="persona" text="yeah probably" />);

    await user.click(screen.getByRole("button", { name: /copy message/i }));

    expect(writeText).toHaveBeenCalledTimes(1);
    expect(writeText).toHaveBeenCalledWith("yeah probably");
  });

  it("shows a copied affordance after a successful copy", async () => {
    const user = userEvent.setup();
    installClipboardMock();
    render(<Bubble role="persona" text="hello" />);

    await user.click(screen.getByRole("button", { name: /copy message/i }));

    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: /copied/i }),
      ).toBeInTheDocument(),
    );
  });

  it("is not rendered for error bubbles", () => {
    render(<Bubble role="persona" text="something blew up" variant="error" />);
    expect(
      screen.queryByRole("button", { name: /copy/i }),
    ).not.toBeInTheDocument();
  });
});

describe("TypingBubble", () => {
  it("renders three animated dots labelled as typing", () => {
    const { container } = render(<TypingBubble />);
    const bubble = screen.getByLabelText(/typing/i);
    expect(bubble).toBeInTheDocument();
    expect(container.querySelectorAll(".bubble--typing span")).toHaveLength(3);
  });
});
