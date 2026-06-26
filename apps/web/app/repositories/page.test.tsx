// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const getRegisteredRepositoriesMock = vi.fn();
const replaceMock = vi.fn();
const useAuthMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: replaceMock }),
}));

vi.mock("../../api/github", () => ({
  getRegisteredRepositories: (...args: unknown[]) => getRegisteredRepositoriesMock(...args),
}));

vi.mock("../../features/auth/auth-hooks", () => ({
  useAuth: () => useAuthMock(),
}));

import RepositoriesPage from "./page";

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

beforeEach(() => {
  useAuthMock.mockReturnValue({ loading: false, session: { access_token: "sample" } });
  getRegisteredRepositoriesMock.mockResolvedValue([registeredRepository]);
});

afterEach(() => {
  cleanup();
  getRegisteredRepositoriesMock.mockReset();
  replaceMock.mockReset();
  useAuthMock.mockReset();
});

describe("RepositoriesPage", () => {
  it("redirects unauthenticated users", async () => {
    useAuthMock.mockReturnValue({ loading: false, session: null });

    render(<RepositoriesPage />);

    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith("/login"));
  });

  it("renders registered repositories only", async () => {
    render(<RepositoriesPage />);

    expect(screen.getByText("Registered repositories")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("RepoMind_AI")).toBeInTheDocument());
    expect(screen.getByText("Karthikrnaik24/RepoMind_AI")).toBeInTheDocument();
    expect(screen.getByText("PENDING")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open Dashboard" })).toHaveAttribute(
      "href",
      "/repositories/local-repository-id",
    );
    expect(getRegisteredRepositoriesMock).toHaveBeenCalledWith(
      expect.objectContaining({ getSession: expect.any(Function) }),
    );
  });

  it("renders an empty state when no repositories are registered", async () => {
    getRegisteredRepositoriesMock.mockResolvedValue([]);

    render(<RepositoriesPage />);

    await waitFor(() => expect(screen.getByText("No registered repositories yet")).toBeInTheDocument());
  });

  it("renders a retryable error state", async () => {
    getRegisteredRepositoriesMock
      .mockRejectedValueOnce(new Error("failed"))
      .mockResolvedValueOnce([registeredRepository]);

    render(<RepositoriesPage />);

    await waitFor(() =>
      expect(
        screen.getByText("Registered repositories could not be loaded. Please retry."),
      ).toBeInTheDocument(),
    );
    fireEvent.click(screen.getByRole("button", { name: /Retry/i }));

    await waitFor(() => expect(screen.getByText("RepoMind_AI")).toBeInTheDocument());
  });
});