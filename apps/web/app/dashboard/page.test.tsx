// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const getGitHubRepositoriesMock = vi.fn();
const replaceMock = vi.fn();
const useAuthMock = vi.fn();
const useSearchParamsMock = vi.fn(() => new URLSearchParams());

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: replaceMock }),
  useSearchParams: () => useSearchParamsMock(),
}));

vi.mock("../../api/github", () => ({
  getGitHubRepositories: (...args: unknown[]) => getGitHubRepositoriesMock(...args),
}));

vi.mock("../../features/auth/auth-hooks", () => ({
  useAuth: () => useAuthMock(),
}));

import DashboardPage from "./page";

const repository = {
  id: 123,
  name: "RepoMind_AI",
  full_name: "Karthikrnaik24/RepoMind_AI",
  owner: {
    id: 42,
    login: "Karthikrnaik24",
    type: "User",
    avatar_url: "https://example.com/avatar.png",
    html_url: "https://github.com/Karthikrnaik24",
  },
  private: true,
  visibility: "private",
  language: "TypeScript",
  default_branch: "main",
  updated_at: "2026-06-26T11:00:00Z",
  description: "AI software engineer for GitHub repositories",
  html_url: "https://github.com/Karthikrnaik24/RepoMind_AI",
  permissions: {
    admin: true,
    maintain: true,
    push: true,
    triage: true,
    pull: true,
  },
};

function mockAuthenticatedDashboard(identities = [{ provider: "google" }, { provider: "github" }]) {
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
      identities,
      user_metadata: {
        avatar_url: "https://example.com/avatar.png",
        full_name: "Ada Engineer",
      },
    },
  });
  return { refreshSession };
}

beforeEach(() => {
  getGitHubRepositoriesMock.mockResolvedValue({ success: true, data: [repository], meta: {} });
});

afterEach(() => {
  cleanup();
  getGitHubRepositoriesMock.mockReset();
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

  it("renders Google and GitHub authentication status", async () => {
    const { refreshSession } = mockAuthenticatedDashboard([{ provider: "google" }]);

    render(<DashboardPage />);

    expect(screen.getByText("Ada Engineer")).toBeInTheDocument();
    expect(screen.getByText("engineer@example.com")).toBeInTheDocument();
    expect(screen.getByAltText("User avatar")).toBeInTheDocument();
    expect(screen.getByText("Authentication Status")).toBeInTheDocument();
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

  it("renders repository cards for linked GitHub users", async () => {
    mockAuthenticatedDashboard();

    render(<DashboardPage />);

    expect(screen.getByText("Repositories")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("RepoMind_AI")).toBeInTheDocument());
    expect(screen.getByText("Karthikrnaik24")).toBeInTheDocument();
    expect(screen.getByText("AI software engineer for GitHub repositories")).toBeInTheDocument();
    expect(screen.getByText("TypeScript")).toBeInTheDocument();
    expect(screen.getByText("private")).toBeInTheDocument();
    expect(getGitHubRepositoriesMock).toHaveBeenCalledWith(
      expect.objectContaining({ getSession: expect.any(Function) }),
      expect.objectContaining({ page: 1, perPage: 12, visibility: "all" }),
    );
  });

  it("shows skeleton loaders while repositories load", () => {
    getGitHubRepositoriesMock.mockReturnValue(new Promise(() => undefined));
    mockAuthenticatedDashboard();

    render(<DashboardPage />);

    expect(screen.getByText("Repositories")).toBeInTheDocument();
    expect(document.querySelectorAll(".animate-pulse").length).toBeGreaterThan(0);
  });

  it("shows an empty state when no repositories are returned", async () => {
    getGitHubRepositoriesMock.mockResolvedValue({ success: true, data: [], meta: {} });
    mockAuthenticatedDashboard();

    render(<DashboardPage />);

    await waitFor(() => expect(screen.getByText("No repositories to show")).toBeInTheDocument());
    expect(screen.getByText("No repositories were found for this GitHub account.")).toBeInTheDocument();
  });

  it("sends search and visibility filters to the backend", async () => {
    mockAuthenticatedDashboard();

    render(<DashboardPage />);
    fireEvent.change(screen.getByPlaceholderText("Search repositories"), {
      target: { value: "RepoMind" },
    });
    fireEvent.change(screen.getByLabelText("Visibility filter"), { target: { value: "private" } });

    await waitFor(() =>
      expect(getGitHubRepositoriesMock).toHaveBeenLastCalledWith(
        expect.objectContaining({ getSession: expect.any(Function) }),
        expect.objectContaining({ search: "RepoMind", visibility: "private" }),
      ),
    );
  });

  it("shows friendly repository discovery errors", async () => {
    getGitHubRepositoriesMock.mockRejectedValue(new Error("rate limited"));
    mockAuthenticatedDashboard();

    render(<DashboardPage />);

    await waitFor(() =>
      expect(screen.getByText("Repository discovery is unavailable right now.")).toBeInTheDocument(),
    );
  });

  it("shows friendly GitHub linking errors", () => {
    useSearchParamsMock.mockReturnValue(new URLSearchParams("github_link_error=oauth_cancelled"));
    mockAuthenticatedDashboard([{ provider: "google" }]);

    render(<DashboardPage />);

    expect(screen.getByText("GitHub linking was cancelled.")).toBeInTheDocument();
  });
});