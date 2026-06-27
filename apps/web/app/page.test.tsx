// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

const useAuthMock = vi.fn();

vi.mock("../features/auth/auth-hooks", () => ({
  useAuth: () => useAuthMock(),
}));

import HomePage from "./page";

afterEach(() => {
  cleanup();
  useAuthMock.mockReset();
});

describe("HomePage", () => {
  it("shows Google and GitHub login buttons when unauthenticated", () => {
    useAuthMock.mockReturnValue({
      loading: false,
      session: null,
      signInWithGitHub: vi.fn(),
      signInWithGoogle: vi.fn(),
    });

    render(<HomePage />);

    expect(screen.getByRole("button", { name: "Continue with Google" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Continue with GitHub" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Go to Dashboard" })).not.toBeInTheDocument();
  });

  it("hides login buttons when authenticated", () => {
    useAuthMock.mockReturnValue({
      loading: false,
      session: { access_token: "sample-token" },
      signInWithGitHub: vi.fn(),
      signInWithGoogle: vi.fn(),
    });

    render(<HomePage />);

    expect(screen.queryByRole("button", { name: "Continue with Google" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Continue with GitHub" })).not.toBeInTheDocument();
  });

  it("shows dashboard and repositories CTAs when authenticated", () => {
    useAuthMock.mockReturnValue({
      loading: false,
      session: { access_token: "sample-token" },
      signInWithGitHub: vi.fn(),
      signInWithGoogle: vi.fn(),
    });

    render(<HomePage />);

    expect(screen.getByRole("link", { name: "Go to Dashboard" })).toHaveAttribute(
      "href",
      "/dashboard",
    );
    expect(screen.getByRole("link", { name: "Repositories" })).toHaveAttribute(
      "href",
      "/repositories",
    );
  });

  it("does not flash login buttons while authentication state is loading", () => {
    useAuthMock.mockReturnValue({
      loading: true,
      session: null,
      signInWithGitHub: vi.fn(),
      signInWithGoogle: vi.fn(),
    });

    render(<HomePage />);

    expect(screen.getByLabelText("Loading authentication state")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Continue with Google" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Continue with GitHub" })).not.toBeInTheDocument();
  });
});
