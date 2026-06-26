// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const setThemeMock = vi.fn();

vi.mock("next-themes", () => ({
  useTheme: () => ({ resolvedTheme: "dark", setTheme: setThemeMock }),
}));

import { ThemeToggle } from "./theme-toggle";

describe("ThemeToggle", () => {
  it("renders an accessible toggle and switches without a page reload", async () => {
    render(<ThemeToggle />);

    const toggle = await screen.findByRole("button", { name: "Switch to light mode" });
    fireEvent.click(toggle);

    expect(setThemeMock).toHaveBeenCalledWith("light");
  });
});
