// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const replaceMock = vi.fn();
const useAuthMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: replaceMock }),
}));

vi.mock("../../features/auth/auth-hooks", () => ({
  useAuth: () => useAuthMock(),
}));

import DashboardPage from "./page";

describe("DashboardPage", () => {
  it("redirects when the user is logged out", async () => {
    useAuthMock.mockReturnValue({ loading: false, session: null });

    render(<DashboardPage />);

    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith("/login"));
  });

  it("renders signed-in Google user details", () => {
    useAuthMock.mockReturnValue({
      loading: false,
      session: { access_token: "sample" },
      signOut: vi.fn(),
      user: {
        app_metadata: { provider: "google" },
        email: "engineer@example.com",
        user_metadata: {
          avatar_url: "https://example.com/avatar.png",
          full_name: "Ada Engineer",
        },
      },
    });

    render(<DashboardPage />);

    expect(screen.getByText("Ada Engineer")).toBeInTheDocument();
    expect(screen.getByText("engineer@example.com")).toBeInTheDocument();
    expect(screen.getByText("Provider: google")).toBeInTheDocument();
    expect(screen.getByAltText("User avatar")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Log out" })).toBeInTheDocument();
  });
});
