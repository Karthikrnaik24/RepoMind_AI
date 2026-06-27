// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next-themes", () => ({
  useTheme: () => ({ resolvedTheme: "light", setTheme: vi.fn() }),
}));

vi.mock("../features/auth/auth-hooks", () => ({
  useAuth: () => ({ loading: false, session: null, signOut: vi.fn() }),
}));

import { SiteNav } from "./site-nav";

describe("SiteNav", () => {
  it("renders product navigation, search, auth actions, and theme toggles", async () => {
    render(<SiteNav />);

    expect(screen.getByRole("link", { name: "Features" })).toHaveAttribute("href", "/#features");
    expect(screen.getByRole("link", { name: "Docs" })).toHaveAttribute("href", "/#docs");
    expect(screen.getByRole("link", { name: /Pricing/i })).toHaveAttribute("href", "/#pricing");
    expect(screen.getByRole("searchbox", { name: "Search repositories" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Sign In" })).toHaveAttribute("href", "/login");
    expect(screen.getByRole("link", { name: "Sign Up" })).toHaveAttribute("href", "/login");
    expect(await screen.findAllByRole("button", { name: "Switch to dark mode" })).toHaveLength(2);
  });
});
