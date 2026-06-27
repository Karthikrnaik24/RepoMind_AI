// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

const signInWithGitHubMock = vi.fn();
const signInWithGoogleMock = vi.fn();

vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock("../../features/auth/auth-hooks", () => ({
  useAuth: () => ({
    signInWithGitHub: signInWithGitHubMock,
    signInWithGoogle: signInWithGoogleMock,
  }),
}));

import LoginPage from "./page";

afterEach(() => {
  cleanup();
  signInWithGitHubMock.mockReset();
  signInWithGoogleMock.mockReset();
});

describe("LoginPage", () => {
  it("triggers Google OAuth from the Google button", () => {
    render(<LoginPage />);

    fireEvent.click(screen.getByRole("button", { name: "Continue with Google" }));

    expect(signInWithGoogleMock).toHaveBeenCalledOnce();
    expect(screen.getByRole("button", { name: "Continue with GitHub" })).toBeEnabled();
    expect(
      screen.getByText(/keeps them connected to one account/i),
    ).toBeInTheDocument();
  });

  it("triggers GitHub OAuth from the GitHub button", () => {
    render(<LoginPage />);

    fireEvent.click(screen.getByRole("button", { name: "Continue with GitHub" }));

    expect(signInWithGitHubMock).toHaveBeenCalledOnce();
  });
});

