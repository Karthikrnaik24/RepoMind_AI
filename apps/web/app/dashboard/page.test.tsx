// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const getGitHubRepositoriesMock = vi.fn();
const getRegisteredRepositoriesMock = vi.fn();
const registerGitHubRepositoryMock = vi.fn();
const replaceMock = vi.fn();
const useAuthMock = vi.fn();
const useSearchParamsMock = vi.fn(() => new URLSearchParams());

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: replaceMock }),
  useSearchParams: () => useSearchParamsMock(),
}));

vi.mock("../../api/github", () => {
  class MockGitHubRepositoryDiscoveryError extends Error {
    code: string;

    constructor(code: string) {
      super(code);
      this.code = code;
    }
  }

  return {
    getGitHubRepositories: (...args: unknown[]) => getGitHubRepositoriesMock(...args),
    getRegisteredRepositories: (...args: unknown[]) => getRegisteredRepositoriesMock(...args),
    registerGitHubRepository: (...args: unknown[]) => registerGitHubRepositoryMock(...args),
    GitHubRepositoryDiscoveryError: MockGitHubRepositoryDiscoveryError,
  };
});

vi.mock("../../features/auth/auth-hooks", () => ({
  useAuth: () => useAuthMock(),
}));

import { GitHubRepositoryDiscoveryError } from "../../api/github";

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

const registeredRepository = {
  id: "local-repository-id",
  owner_user_id: "local-user-id",
  github_repository_id: "123",
  name: "RepoMind_AI",
  full_name: "Karthikrnaik24/RepoMind_AI",
  owner_login: "Karthikrnaik24",
  default_branch: "main",
  visibility: "private",
  language: "TypeScript",
  description: "AI software engineer for GitHub repositories",
  html_url: "https://github.com/Karthikrnaik24/RepoMind_AI",
  registered_at: "2026-06-26T10:00:00Z",
  sync_status: "PENDING",
  created_at: "2026-06-26T10:00:00Z",
  updated_at: "2026-06-26T10:00:00Z",
};

function mockAuthenticatedDashboard(identities = [{ provider: "google" }, { provider: "github" }]) {
  const session = { access_token: "sample", provider_token: "github-provider-token" };
  const refreshSession = vi.fn(async () => session);
  useAuthMock.mockReturnValue({
    authError: null,
    linkGitHubIdentity: vi.fn(),
    loading: false,
    refreshSession,
    session,
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
  getRegisteredRepositoriesMock.mockResolvedValue([]);
  registerGitHubRepositoryMock.mockResolvedValue(registeredRepository);
});

afterEach(() => {
  cleanup();
  getGitHubRepositoriesMock.mockReset();
  getRegisteredRepositoriesMock.mockReset();
  registerGitHubRepositoryMock.mockReset();
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
    await waitFor(() => expect(refreshSession).toHaveBeenCalled());
  });

  it("starts GitHub identity linking from the dashboard", () => {
    const linkGitHubIdentity = vi.fn();
    useAuthMock.mockReturnValue({
      authError: null,
      linkGitHubIdentity,
      loading: false,
      refreshSession: vi.fn(async () => ({ access_token: "sample", provider_token: "github-provider-token" })),
      session: { access_token: "sample", provider_token: "github-provider-token" },
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
    expect(screen.getByAltText("Karthikrnaik24 avatar")).toBeInTheDocument();
    expect(screen.getByText("private")).toBeInTheDocument();
    expect(screen.getByText("main")).toBeInTheDocument();
    expect(screen.getByText("Searching across repositories with GitHub Search.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Register Repository" })).toBeInTheDocument();
    expect(getGitHubRepositoriesMock).toHaveBeenCalledWith(
      expect.objectContaining({ getSession: expect.any(Function) }),
      expect.objectContaining({ page: 1, perPage: 12, visibility: "all" }),
    );
    expect(getRegisteredRepositoriesMock).toHaveBeenCalledWith(
      expect.objectContaining({ getSession: expect.any(Function) }),
    );
  });

  it("registers a repository from the dashboard", async () => {
    mockAuthenticatedDashboard();

    render(<DashboardPage />);
    const button = await screen.findByRole("button", { name: "Register Repository" });
    fireEvent.click(button);

    await waitFor(() => expect(registerGitHubRepositoryMock).toHaveBeenCalledOnce());
    expect(registerGitHubRepositoryMock).toHaveBeenCalledWith(
      expect.objectContaining({ getSession: expect.any(Function) }),
      {
        github_repository_id: "123",
        full_name: "Karthikrnaik24/RepoMind_AI",
        default_branch: "main",
      },
    );
    await waitFor(() => expect(screen.getByRole("button", { name: /Registered/i })).toBeDisabled());
  });

  it("shows registered repositories as disabled", async () => {
    getRegisteredRepositoriesMock.mockResolvedValue([registeredRepository]);
    mockAuthenticatedDashboard();

    render(<DashboardPage />);

    await waitFor(() => expect(screen.getByRole("button", { name: /Registered/i })).toBeDisabled());
    expect(screen.getAllByText("Registered").length).toBeGreaterThanOrEqual(1);
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

    await waitFor(() =>
      expect(screen.getByText("GitHub account has no repositories")).toBeInTheDocument(),
    );
    expect(screen.getByText("No repositories were returned for this linked GitHub account.")).toBeInTheDocument();
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
    getGitHubRepositoriesMock.mockRejectedValue(new Error("repository fetch failed"));
    mockAuthenticatedDashboard();

    render(<DashboardPage />);

    await waitFor(() =>
      expect(screen.getByText("Repository fetch failed. Please try again.")).toBeInTheDocument(),
    );
  });

  it("shows search empty state messaging", async () => {
    getGitHubRepositoriesMock.mockResolvedValue({ success: true, data: [], meta: {} });
    mockAuthenticatedDashboard();

    render(<DashboardPage />);
    fireEvent.change(screen.getByPlaceholderText("Search repositories"), {
      target: { value: "missing" },
    });

    await waitFor(() => expect(screen.getByText("Search returned no matches")).toBeInTheDocument());
    expect(
      screen.getByText("GitHub Search did not return repositories for this name and visibility filter."),
    ).toBeInTheDocument();
  });

  it("retries repository discovery after an error", async () => {
    getGitHubRepositoriesMock
      .mockRejectedValueOnce(new Error("repository fetch failed"))
      .mockResolvedValueOnce({ success: true, data: [repository], meta: {} });
    mockAuthenticatedDashboard();

    render(<DashboardPage />);
    await waitFor(() =>
      expect(screen.getByText("Repository fetch failed. Please try again.")).toBeInTheDocument(),
    );
    fireEvent.click(screen.getByRole("button", { name: /Retry/i }));

    await waitFor(() => expect(screen.getByText("RepoMind_AI")).toBeInTheDocument());
  });

  it("guides users to reconnect GitHub when the provider token is unavailable", async () => {
    const linkGitHubIdentity = vi.fn();
    getGitHubRepositoriesMock.mockRejectedValue(
      new GitHubRepositoryDiscoveryError("reconnect_required"),
    );
    useAuthMock.mockReturnValue({
      authError: null,
      linkGitHubIdentity,
      loading: false,
      refreshSession: vi.fn(async () => ({ access_token: "sample" })),
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

    await waitFor(() =>
      expect(screen.getByText("Reconnect GitHub to refresh repository access.")).toBeInTheDocument(),
    );
    fireEvent.click(screen.getByRole("button", { name: /Reconnect GitHub/i }));

    expect(linkGitHubIdentity).toHaveBeenCalledOnce();
  });

  it("shows friendly GitHub linking errors", () => {
    useSearchParamsMock.mockReturnValue(new URLSearchParams("github_link_error=oauth_cancelled"));
    mockAuthenticatedDashboard([{ provider: "google" }]);

    render(<DashboardPage />);

    expect(screen.getByText("GitHub connection was cancelled. You can try again whenever you are ready.")).toBeInTheDocument();
  });
});


