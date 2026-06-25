// @vitest-environment jsdom

import type { ReactNode } from "react";
import React from "react";
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("../../features/auth/require-auth", () => ({
  RequireAuth: ({ children }: { children: ReactNode }) => <div data-testid="auth-guard">{children}</div>,
}));

vi.mock("../../features/auth/auth-hooks", () => ({
  useAuth: () => ({
    signOut: vi.fn(),
    user: { email: "engineer@example.com" },
  }),
}));

import DashboardPage from "./page";

describe("DashboardPage", () => {
  it("renders inside the auth guard", () => {
    render(<DashboardPage />);

    expect(screen.getByTestId("auth-guard")).toBeInTheDocument();
    expect(screen.getByText("Signed in as engineer@example.com")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Log out" })).toBeInTheDocument();
  });
});
