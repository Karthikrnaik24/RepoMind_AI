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
export type GitHubRepositoryDiscoveryErrorCode =
  | "github_unavailable"
  | "rate_limited"
  | "token_expired"
  | "fetch_failed";

export class GitHubRepositoryDiscoveryError extends Error {
  code: GitHubRepositoryDiscoveryErrorCode;

  constructor(code: GitHubRepositoryDiscoveryErrorCode) {
    super(code);
    this.name = "GitHubRepositoryDiscoveryError";
    this.code = code;
  }
}

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

function getRepositoryErrorCode(status: number): GitHubRepositoryDiscoveryErrorCode {
  if (status === 401) {
    return "token_expired";
  }

  if (status === 429) {
    return "rate_limited";
  }

  if (status >= 500) {
    return "github_unavailable";
  }

  return "fetch_failed";
}

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
    throw new GitHubRepositoryDiscoveryError(getRepositoryErrorCode(response.status));
  }

  return (await response.json()) as ApiSuccessEnvelope<GitHubRepositorySummary[]>;
}