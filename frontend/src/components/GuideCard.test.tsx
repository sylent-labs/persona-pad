import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";

import { GuideCard } from "./GuideCard";

const FIRST_TIP = "lead with availability";
const TIPS = [
  FIRST_TIP,
  "do not overcommit on dates",
  "keep it one line",
  "ask what they need before saying yes",
];

describe("GuideCard", () => {
  it("shows the welcome prompt before any message", () => {
    render(<GuideCard tips={[]} pending={false} />);
    expect(
      screen.getByText(/lay out how Van Keith would reply/i),
    ).toBeInTheDocument();
    expect(screen.queryByText(FIRST_TIP)).not.toBeInTheDocument();
  });

  it("renders every tip and the updated status when populated", () => {
    render(<GuideCard tips={TIPS} pending={false} />);
    for (const tip of TIPS) {
      expect(screen.getByText(tip)).toBeInTheDocument();
    }
    expect(screen.getByText(/Updated for your last message/i)).toBeInTheDocument();
  });

  it("shows the skeleton while pending, hiding tips and status", () => {
    const { container } = render(<GuideCard tips={TIPS} pending />);
    expect(container.querySelector(".guide-card__skeleton")).not.toBeNull();
    expect(screen.queryByText(FIRST_TIP)).not.toBeInTheDocument();
    expect(
      screen.queryByText(/Updated for your last message/i),
    ).not.toBeInTheDocument();
  });
});
