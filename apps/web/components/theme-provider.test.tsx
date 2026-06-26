// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ThemeProvider } from "./theme-provider";

beforeEach(() => {
  Object.defineProperty(window, "matchMedia", {
    configurable: true,
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      addEventListener: vi.fn(),
      addListener: vi.fn(),
      dispatchEvent: vi.fn(),
      matches: false,
      media: query,
      onchange: null,
      removeEventListener: vi.fn(),
      removeListener: vi.fn(),
    })),
  });
});

describe("ThemeProvider", () => {
  it("renders children while enabling app-level theme context", () => {
    render(
      <ThemeProvider>
        <div>Theme-ready content</div>
      </ThemeProvider>,
    );

    expect(screen.getByText("Theme-ready content")).toBeInTheDocument();
  });
});
