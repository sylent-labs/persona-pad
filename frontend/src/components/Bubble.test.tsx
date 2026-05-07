import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";

import { Bubble, TypingBubble } from "./Bubble";

describe("Bubble", () => {
  it("renders user bubble text and applies the user role class", () => {
    const { container } = render(<Bubble role="user" text="hi there" tail />);
    expect(screen.getByText("hi there")).toBeInTheDocument();
    const bubble = container.querySelector(".bubble");
    expect(bubble?.className).toContain("bubble--user");
    expect(bubble?.className).toContain("bubble--tail");
  });

  it("renders persona bubble text and applies the persona role class", () => {
    const { container } = render(
      <Bubble role="persona" text="yeah probably" />,
    );
    expect(screen.getByText("yeah probably")).toBeInTheDocument();
    const bubble = container.querySelector(".bubble");
    expect(bubble?.className).toContain("bubble--persona");
    expect(bubble?.className).not.toContain("bubble--tail");
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
