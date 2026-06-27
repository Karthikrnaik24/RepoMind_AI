// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const getRegisteredRepositoriesMock = vi.fn();
const refreshRegisteredRepositoryMock = vi.fn();
const unregisterRegisteredRepositoryMock = vi.fn();
const updateRegisteredRepositorySettingsMock = vi.fn();
const replaceMock = vi.fn();
const useAuthMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: replaceMock }),
}));

vi.mock("../../api/github", () => ({
  getRegisteredRepositories: (...args: unknown[]) => getRegisteredRepositoriesMock(...args),
  refreshRegisteredRepository: (...args: unknown[]) => refreshRegisteredRepositoryMock(...args),
  unregisterRegisteredRepository: (...args: unknown[]) => unregisterRegisteredRepositoryMock(...args),
  updateRegisteredRepositorySettings: (...args: unknown[]) =>
    updateRegisteredRepositorySettingsMock(...args),
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
  display_name: null,
  favorite: false,
  notes: null,
  language: "TypeScript",
  description: "AI software engineer for GitHub repositories",
  html_url: "https://github.com/Karthikrnaik24/RepoMind_AI",
  registered_at: "2026-06-26T10:00:00Z",
  sync_status: "PENDING",
  last_synced_at: null,
  github_updated_at: "2026-06-26T11:00:00Z",
  created_at: "2026-06-26T10:00:00Z",
  updated_at: "2026-06-26T10:00:00Z",
};

beforeEach(() => {
  useAuthMock.mockReturnValue({ loading: false, session: { access_token: "sample" } });
  getRegisteredRepositoriesMock.mockResolvedValue([registeredRepository]);
  refreshRegisteredRepositoryMock.mockResolvedValue({
    ...registeredRepository,
    sync_status: "READY",
    last_synced_at: "2026-06-27T10:00:00Z",
  });
  updateRegisteredRepositorySettingsMock.mockResolvedValue({
    ...registeredRepository,
    favorite: true,
    display_name: "Production RepoMind",
    notes: "Critical product repository",
  });
  unregisterRegisteredRepositoryMock.mockResolvedValue(undefined);
});

afterEach(() => {
  cleanup();
  getRegisteredRepositoriesMock.mockReset();
  refreshRegisteredRepositoryMock.mockReset();
  unregisterRegisteredRepositoryMock.mockReset();
  updateRegisteredRepositorySettingsMock.mockReset();
  replaceMock.mockReset();
  useAuthMock.mockReset();
});

describe("RepositoriesPage", () => {
  it("redirects unauthenticated users", async () => {
    useAuthMock.mockReturnValue({ loading: false, session: null });

    render(<RepositoriesPage />);

    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith("/login"));
  });

  it("renders registered repositories with management actions", async () => {
    render(<RepositoriesPage />);

    expect(screen.getByText("Registered repositories")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("RepoMind_AI")).toBeInTheDocument());
    expect(screen.getByText("Karthikrnaik24/RepoMind_AI")).toBeInTheDocument();
    expect(screen.getByText("PENDING")).toBeInTheDocument();
    expect(screen.getByText("Last synchronized Not synchronized yet")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Favorite" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Refresh" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Settings" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Unregister" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open Dashboard" })).toHaveAttribute(
      "href",
      "/repositories/local-repository-id",
    );
    expect(getRegisteredRepositoriesMock).toHaveBeenCalledWith(
      expect.objectContaining({ getSession: expect.any(Function) }),
    );
  });

  it("toggles favorite status", async () => {
    render(<RepositoriesPage />);

    fireEvent.click(await screen.findByRole("button", { name: "Favorite" }));

    await waitFor(() => expect(updateRegisteredRepositorySettingsMock).toHaveBeenCalledOnce());
    expect(updateRegisteredRepositorySettingsMock).toHaveBeenCalledWith(
      expect.objectContaining({ getSession: expect.any(Function) }),
      "local-repository-id",
      { favorite: true },
    );
    await waitFor(() => expect(screen.getByText("Production RepoMind")).toBeInTheDocument());
  });

  it("saves repository settings from the settings panel", async () => {
    render(<RepositoriesPage />);

    fireEvent.click(await screen.findByRole("button", { name: "Settings" }));
    fireEvent.change(screen.getByLabelText("Alias"), { target: { value: "Production RepoMind" } });
    fireEvent.change(screen.getByLabelText("Notes"), {
      target: { value: "Critical product repository" },
    });
    fireEvent.click(screen.getByLabelText("Favorite repository"));
    fireEvent.click(screen.getByRole("button", { name: "Save Settings" }));

    await waitFor(() => expect(updateRegisteredRepositorySettingsMock).toHaveBeenCalledOnce());
    expect(updateRegisteredRepositorySettingsMock).toHaveBeenCalledWith(
      expect.objectContaining({ getSession: expect.any(Function) }),
      "local-repository-id",
      {
        display_name: "Production RepoMind",
        favorite: true,
        notes: "Critical product repository",
      },
    );
  });

  it("refreshes repository metadata", async () => {
    render(<RepositoriesPage />);

    fireEvent.click(await screen.findByRole("button", { name: "Refresh" }));

    await waitFor(() => expect(refreshRegisteredRepositoryMock).toHaveBeenCalledOnce());
    expect(refreshRegisteredRepositoryMock).toHaveBeenCalledWith(
      expect.objectContaining({ getSession: expect.any(Function) }),
      "local-repository-id",
    );
    await waitFor(() => expect(screen.getByText("READY")).toBeInTheDocument());
  });

  it("shows confirmation before unregistering a repository", async () => {
    render(<RepositoriesPage />);

    fireEvent.click(await screen.findByRole("button", { name: "Unregister" }));

    expect(screen.getByRole("alertdialog", { name: /Unregister Karthikrnaik24\/RepoMind_AI/i })).toBeInTheDocument();
    expect(screen.getByRole("alertdialog")).toHaveTextContent(/GitHub repository will not be deleted/);
    fireEvent.click(screen.getByRole("button", { name: "Confirm Unregister" }));

    await waitFor(() => expect(unregisterRegisteredRepositoryMock).toHaveBeenCalledOnce());
    await waitFor(() => expect(screen.queryByText("RepoMind_AI")).not.toBeInTheDocument());
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
