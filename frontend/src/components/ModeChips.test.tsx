import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ModeChips } from "./ModeChips";

describe("ModeChips", () => {
  it("marks the current mode chip as checked", () => {
    render(<ModeChips mode="raw" onModeChange={vi.fn()} />);
    expect(screen.getByRole("radio", { name: /raw/i })).toBeChecked();
  });

  it("calls onModeChange when a different chip is tapped", async () => {
    const onModeChange = vi.fn();
    const user = userEvent.setup();
    render(<ModeChips mode="raw" onModeChange={onModeChange} />);

    await user.click(screen.getByRole("radio", { name: /professional/i }));

    expect(onModeChange).toHaveBeenCalledWith("professional");
  });
});
