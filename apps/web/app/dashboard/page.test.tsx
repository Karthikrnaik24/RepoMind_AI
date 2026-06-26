// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const getGitHubTokenDebugStatusMock = vi.fn();
const replaceMock = vi.fn();
const useAuthMock = vi.fn();
const useSearchParamsMock = vi.fn(() => new URLSearchParams());

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: replaceMock }),
  useSearchParams: () => useSearchParamsMock(),
}));

vi.mock("../../api/github", () => ({
  getGitHubTokenDebugStatus: (...args: unknown[]) => getGitHubTokenDebugStatusMock(...args),
}));

vi.mock("../../features/auth/auth-hooks", () => ({
  useAuth: () => useAuthMock(),
}));

import DashboardPage from "./page";

beforeEach(() => {
  getGitHubTokenDebugStatusMock.mockResolvedValue({
    github_linked: false,
    token_available: false,
    provider: "github",
  });
});

afterEach(() => {
  cleanup();
  getGitHubTokenDebugStatusMock.mockReset();
  getGitHubTokenDebugStatusMock.mockResolvedValue({
    github_linked: false,
    token_available: false,
    provider: "github",
  });
  replaceMock.mockReset();
  useAuthMock.mockReset();
  useSearchParamsMock.mockReturnValue(new URLSearchParams());
});

describe("DashboardPage", () => {
  it("redirects when the user is logged out", async () => {
    useAuthMock.mockReturnValue({ loading: false, session: null });

    render(<DashboardPage />);

    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith("/login"));
  });

  it("renders Google as connected and GitHub as not connected", async () => {
    const refreshSession = vi.fn();
    useAuthMock.mockReturnValue({
      authError: null,
      linkGitHubIdentity: vi.fn(),
      loading: false,
      refreshSession,
      session: { access_token: "sample" },
      signOut: vi.fn(),
      user: {
        app_metadata: { provider: "google" },
        email: "engineer@example.com",
        identities: [{ provider: "google" }],
        user_metadata: {
          avatar_url: "https://example.com/avatar.png",
          full_name: "Ada Engineer",
        },
      },
    });

    render(<DashboardPage />);

    expect(screen.getByText("Ada Engineer")).toBeInTheDocument();
    expect(screen.getByText("engineer@example.com")).toBeInTheDocument();
    expect(screen.getByAltText("User avatar")).toBeInTheDocument();
    expect(screen.getByText("Authentication Status")).toBeInTheDocument();
    expect(screen.getByText("Google")).toBeInTheDocument();
    expect(screen.getByText("GitHub")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Connect GitHub/i })).toBeInTheDocument();
    expect(screen.getAllByText("Not Connected").length).toBeGreaterThanOrEqual(1);
    await waitFor(() => expect(refreshSession).toHaveBeenCalledOnce());
  });

  it("starts GitHub identity linking from the dashboard", () => {
    const linkGitHubIdentity = vi.fn();
    useAuthMock.mockReturnValue({
      authError: null,
      linkGitHubIdentity,
      loading: false,
      refreshSession: vi.fn(),
      session: { access_token: "sample" },
      signOut: vi.fn(),
      user: {
        app_metadata: { provider: "google" },
        email: "engineer@example.com",
        identities: [{ provider: "google" }],
        user_metadata: { full_name: "Ada Engineer" },
      },
    });

    render(<DashboardPage />);
    fireEvent.click(screen.getByRole("button", { name: /Connect GitHub/i }));

    expect(linkGitHubIdentity).toHaveBeenCalledOnce();
  });

  it("displays linked Google and GitHub identities", () => {
    useAuthMock.mockReturnValue({
      authError: null,
      linkGitHubIdentity: vi.fn(),
      loading: false,
      refreshSession: vi.fn(),
      session: { access_token: "sample" },
      signOut: vi.fn(),
      user: {
        app_metadata: { provider: "google" },
        email: "engineer@example.com",
        identities: [{ provider: "google" }, { provider: "github" }],
        user_metadata: { full_name: "Ada Engineer" },
      },
    });

    render(<DashboardPage />);

    expect(screen.queryByRole("button", { name: /Connect GitHub/i })).not.toBeInTheDocument();
    expect(screen.getAllByText("Connected").length).toBeGreaterThanOrEqual(2);
  });

  it("shows friendly GitHub linking errors", () => {
    useSearchParamsMock.mockReturnValue(new URLSearchParams("github_link_error=oauth_cancelled"));
    useAuthMock.mockReturnValue({
      authError: null,
      linkGitHubIdentity: vi.fn(),
      loading: false,
      refreshSession: vi.fn(),
      session: { access_token: "sample" },
      signOut: vi.fn(),
      user: {
        app_metadata: { provider: "google" },
        email: "engineer@example.com",
        identities: [{ provider: "google" }],
        user_metadata: { full_name: "Ada Engineer" },
      },
    });

    render(<DashboardPage />);

    expect(screen.getByText("GitHub linking was cancelled.")).toBeInTheDocument();
  });

  it("shows developer-only GitHub token debug status", async () => {
    getGitHubTokenDebugStatusMock.mockResolvedValue({
      github_linked: true,
      token_available: true,
      provider: "github",
    });
    useAuthMock.mockReturnValue({
      authError: null,
      linkGitHubIdentity: vi.fn(),
      loading: false,
      refreshSession: vi.fn(),
      session: { access_token: "sample" },
      signOut: vi.fn(),
      user: {
        app_metadata: { provider: "google" },
        email: "engineer@example.com",
        identities: [{ provider: "google" }, { provider: "github" }],
        user_metadata: { full_name: "Ada Engineer" },
      },
    });

    render(<DashboardPage />);

    expect(screen.getByText("GitHub Token Debug")).toBeInTheDocument();
    await waitFor(() => expect(getGitHubTokenDebugStatusMock).toHaveBeenCalledOnce());
    expect(screen.getByText("GitHub Linked")).toBeInTheDocument();
    expect(screen.getByText("Token Available")).toBeInTheDocument();
    expect(screen.getByText("Provider")).toBeInTheDocument();
    expect(screen.getByText("github")).toBeInTheDocument();
    expect(screen.queryByText("sample")).not.toBeInTheDocument();
  });
});