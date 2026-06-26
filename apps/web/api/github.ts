import type { Session } from "@supabase/supabase-js";

import { createApiClient } from "./client";

export type GitHubTokenDebugStatus = {
  github_linked: boolean;
  token_available: boolean;
  provider: "github";
};

export type GitHubRepositorySummary = {
  id: number;
  name: string;
  full_name: string;
  owner: {
    id: number;
    login: string;
    type: string;
    avatar_url: string | null;
    html_url: string | null;
  };
  private: boolean;
  visibility: string | null;
  language: string | null;
  default_branch: string;
  updated_at: string | null;
  description: string | null;
  html_url: string;
  permissions: {
    admin: boolean;
    maintain: boolean;
    push: boolean;
    triage: boolean;
    pull: boolean;
  };
};

export type GitHubRepositoryVisibility = "all" | "public" | "private";

type ApiSuccessEnvelope<T> = {
  success: true;
  data: T;
  meta: Record<string, unknown>;
};

type GitHubApiOptions = {
  baseUrl?: string;
  fetcher?: typeof fetch;
  getSession: () => Promise<Session | null>;
};

type GitHubRepositoryQuery = {
  page?: number;
  perPage?: number;
  search?: string;
  visibility?: GitHubRepositoryVisibility;
};

export async function getGitHubTokenDebugStatus({
  baseUrl,
  fetcher,
  getSession,
}: GitHubApiOptions): Promise<GitHubTokenDebugStatus> {
  const client = createApiClient({ baseUrl, fetcher, getSession });
  const response = await client.request("/api/v1/github/debug-token", { authenticated: true });

  if (!response.ok) {
    throw new Error("GitHub token debug request failed.");
  }

  const payload = (await response.json()) as ApiSuccessEnvelope<GitHubTokenDebugStatus>;
  return payload.data;
}

export async function getGitHubRepositories(
  { baseUrl, fetcher, getSession }: GitHubApiOptions,
  query: GitHubRepositoryQuery = {},
): Promise<ApiSuccessEnvelope<GitHubRepositorySummary[]>> {
  const client = createApiClient({ baseUrl, fetcher, getSession });
  const searchParams = new URLSearchParams({
    page: String(query.page ?? 1),
    per_page: String(query.perPage ?? 12),
    sort: "updated",
    direction: "desc",
    visibility: query.visibility ?? "all",
  });

  const normalizedSearch = query.search?.trim();
  if (normalizedSearch) {
    searchParams.set("search", normalizedSearch);
  }

  const response = await client.request(`/api/v1/github/repositories?${searchParams.toString()}`, {
    authenticated: true,
  });

  if (!response.ok) {
    throw new Error("GitHub repository discovery request failed.");
  }

  return (await response.json()) as ApiSuccessEnvelope<GitHubRepositorySummary[]>;
}