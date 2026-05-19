import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { Bubble, TypingBubble } from "./Bubble";

describe("Bubble", () => {
  it("renders user bubble text and applies the user role class", () => {
    const { container } = render(
      <Bubble role="user" text="hi there" tail label="option 1: " />,
    );
    expect(screen.getByText("option 1:")).toBeInTheDocument();
    expect(screen.getByText("hi there")).toBeInTheDocument();
    const bubble = container.querySelector(".bubble");
    expect(bubble?.className).toContain("bubble--user");
    expect(bubble?.className).toContain("bubble--tail");
  });

  it("renders persona bubble text and applies the persona role class", () => {
    const { container } = render(
      <Bubble role="persona" text="yeah probably" label="option 2: " />,
    );
    expect(screen.getByText("option 2:")).toBeInTheDocument();
    expect(screen.getByText("yeah probably")).toBeInTheDocument();
    const bubble = container.querySelector(".bubble");
    expect(bubble?.className).toContain("bubble--persona");
    expect(bubble?.className).not.toContain("bubble--tail");
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

  it("copies only the text and leaves out the label prefix", async () => {
    const user = userEvent.setup();
    const writeText = installClipboardMock();
    render(<Bubble role="persona" text="yeah probably" label="option 1: " />);

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
