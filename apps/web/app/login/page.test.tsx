// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const signInWithGoogleMock = vi.fn();

vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock("../../features/auth/auth-hooks", () => ({
  useAuth: () => ({ signInWithGoogle: signInWithGoogleMock }),
}));

import LoginPage from "./page";

describe("LoginPage", () => {
  it("triggers Google OAuth from the Google button", () => {
    render(<LoginPage />);

    fireEvent.click(screen.getByRole("button", { name: "Continue with Google" }));

    expect(signInWithGoogleMock).toHaveBeenCalledOnce();
    expect(screen.getByRole("button", { name: "Continue with GitHub" })).toBeDisabled();
    expect(screen.getByText("GitHub OAuth will be enabled in a later sprint.")).toBeInTheDocument();
  });
});
