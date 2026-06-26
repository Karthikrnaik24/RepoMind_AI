// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const getRegisteredRepositoryMock = vi.fn();
const replaceMock = vi.fn();
const useAuthMock = vi.fn();
const useParamsMock = vi.fn(() => ({ repositoryId: "local-repository-id" }));

vi.mock("next/navigation", () => ({
  useParams: () => useParamsMock(),
  useRouter: () => ({ replace: replaceMock }),
}));

vi.mock("../../../api/github", () => ({
  getRegisteredRepository: (...args: unknown[]) => getRegisteredRepositoryMock(...args),
}));

vi.mock("../../../features/auth/auth-hooks", () => ({
  useAuth: () => useAuthMock(),
}));

import RepositoryDashboardPage from "./page";

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
  useParamsMock.mockReturnValue({ repositoryId: "local-repository-id" });
  getRegisteredRepositoryMock.mockResolvedValue(registeredRepository);
});

afterEach(() => {
  cleanup();
  getRegisteredRepositoryMock.mockReset();
  replaceMock.mockReset();
  useAuthMock.mockReset();
  useParamsMock.mockReset();
});

describe("RepositoryDashboardPage", () => {
  it("redirects unauthenticated users", async () => {
    useAuthMock.mockReturnValue({ loading: false, session: null });

    render(<RepositoryDashboardPage />);

    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith("/login"));
  });

  it("renders repository dashboard metadata and status cards", async () => {
    render(<RepositoryDashboardPage />);

    await waitFor(() => expect(screen.getByText("Repository Dashboard")).toBeInTheDocument());
    expect(screen.getByRole("heading", { name: "RepoMind_AI" })).toBeInTheDocument();
    expect(screen.getByText("Karthikrnaik24/RepoMind_AI")).toBeInTheDocument();
    expect(screen.getByText("Repository Overview")).toBeInTheDocument();
    expect(screen.getByText("Repository Metadata")).toBeInTheDocument();
    expect(screen.getByText("Registration Information")).toBeInTheDocument();
    expect(screen.getByText("Synchronization Status")).toBeInTheDocument();
    expect(screen.getByText("Repository Registered")).toBeInTheDocument();
    expect(screen.getByText("Default Branch")).toBeInTheDocument();
    expect(screen.getAllByText("Available in v0.3").length).toBeGreaterThanOrEqual(3);
    expect(getRegisteredRepositoryMock).toHaveBeenCalledWith(
      expect.objectContaining({ getSession: expect.any(Function) }),
      "local-repository-id",
    );
  });

  it("renders navigation back to the repository list and GitHub link", async () => {
    render(<RepositoryDashboardPage />);

    await waitFor(() => expect(screen.getByText("Repository Dashboard")).toBeInTheDocument());
    expect(screen.getByRole("link", { name: "Back to Repository List" })).toHaveAttribute(
      "href",
      "/repositories",
    );
    expect(screen.getByRole("link", { name: /GitHub/i })).toHaveAttribute(
      "href",
      "https://github.com/Karthikrnaik24/RepoMind_AI",
    );
  });

  it("renders a friendly not found or unauthorized error", async () => {
    getRegisteredRepositoryMock.mockRejectedValue(new Error("not found"));

    render(<RepositoryDashboardPage />);

    await waitFor(() =>
      expect(
        screen.getByText(
          "Repository dashboard could not be loaded. It may not exist or you may not have access.",
        ),
      ).toBeInTheDocument(),
    );
    expect(screen.getByRole("button", { name: /Retry/i })).toBeInTheDocument();
  });

  it("retries repository dashboard loading after an error", async () => {
    getRegisteredRepositoryMock
      .mockRejectedValueOnce(new Error("failed"))
      .mockResolvedValueOnce(registeredRepository);

    render(<RepositoryDashboardPage />);

    await waitFor(() =>
      expect(
        screen.getByText(
          "Repository dashboard could not be loaded. It may not exist or you may not have access.",
        ),
      ).toBeInTheDocument(),
    );
    fireEvent.click(screen.getByRole("button", { name: /Retry/i }));

    await waitFor(() => expect(screen.getByText("Repository Dashboard")).toBeInTheDocument());
  });
});