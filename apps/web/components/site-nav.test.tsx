// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

const useAuthMock = vi.fn();

vi.mock("next-themes", () => ({
  useTheme: () => ({ resolvedTheme: "light", setTheme: vi.fn() }),
}));

vi.mock("../features/auth/auth-hooks", () => ({
  useAuth: () => useAuthMock(),
}));

import { SiteNav } from "./site-nav";

afterEach(() => {
  cleanup();
  useAuthMock.mockReset();
});

describe("SiteNav", () => {
  it("renders product navigation, search, auth actions, and theme toggles when signed out", async () => {
    useAuthMock.mockReturnValue({ loading: false, session: null, signOut: vi.fn() });

    render(<SiteNav />);

    expect(screen.getByRole("link", { name: "RepoMind AI" })).toHaveAttribute("href", "/");
    expect(screen.getByRole("link", { name: "Features" })).toHaveAttribute("href", "/#features");
    expect(screen.getByRole("link", { name: "Docs" })).toHaveAttribute("href", "/#docs");
    expect(screen.getByRole("link", { name: /Pricing/i })).toHaveAttribute("href", "/#pricing");
    expect(screen.getByRole("searchbox", { name: "Search repositories" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Sign In" })).toHaveAttribute("href", "/login");
    expect(screen.getByRole("link", { name: "Sign Up" })).toHaveAttribute("href", "/login");
    expect(await screen.findAllByRole("button", { name: "Switch to dark mode" })).toHaveLength(2);
  });

  it("routes the logo to dashboard and hides sign-in actions when authenticated", () => {
    useAuthMock.mockReturnValue({
      loading: false,
      session: { access_token: "sample-token" },
      signOut: vi.fn(),
    });

    render(<SiteNav />);

    expect(screen.getByRole("link", { name: "RepoMind AI" })).toHaveAttribute(
      "href",
      "/dashboard",
    );
    expect(screen.queryByRole("link", { name: "Sign In" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Sign Up" })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Dashboard" })).toHaveAttribute("href", "/dashboard");
    expect(screen.getByRole("link", { name: "Repositories" })).toHaveAttribute(
      "href",
      "/repositories",
    );
    expect(screen.getByRole("button", { name: "Logout" })).toBeInTheDocument();
  });

  it("does not flash signed-out auth actions while authentication state is loading", () => {
    useAuthMock.mockReturnValue({ loading: true, session: null, signOut: vi.fn() });

    render(<SiteNav />);

    expect(screen.queryByRole("link", { name: "Sign In" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Sign Up" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Logout" })).not.toBeInTheDocument();
  });
});
