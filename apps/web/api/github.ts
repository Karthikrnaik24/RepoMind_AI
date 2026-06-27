import type { Session } from "@supabase/supabase-js";

import { createApiClient } from "./client";

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

export type RepositorySyncStatus = "PENDING" | "READY" | "ERROR";

export type RegisteredRepository = {
  id: string;
  owner_user_id: string;
  github_repository_id: string;
  name: string;
  full_name: string;
  owner_login: string;
  default_branch: string;
  visibility: string;
  display_name: string | null;
  favorite: boolean;
  notes: string | null;
  language: string | null;
  description: string | null;
  html_url: string | null;
  registered_at: string;
  sync_status: RepositorySyncStatus;
  last_synced_at: string | null;
  github_updated_at: string | null;
  created_at: string;
  updated_at: string;
};

export type UpdateRepositorySettingsInput = {
  display_name?: string | null;
  favorite?: boolean;
  notes?: string | null;
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

type RegisterRepositoryInput = {
  github_repository_id: string;
  full_name: string;
  default_branch: string;
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

async function parseSuccess<T>(response: Response): Promise<ApiSuccessEnvelope<T>> {
  return (await response.json()) as ApiSuccessEnvelope<T>;
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

  return parseSuccess<GitHubRepositorySummary[]>(response);
}

export async function registerGitHubRepository(
  { baseUrl, fetcher, getSession }: GitHubApiOptions,
  repository: RegisterRepositoryInput,
): Promise<RegisteredRepository> {
  const client = createApiClient({ baseUrl, fetcher, getSession });
  const response = await client.request("/api/v1/repositories/register", {
    authenticated: true,
    body: JSON.stringify(repository),
    headers: { "Content-Type": "application/json" },
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Repository registration failed.");
  }

  const payload = await parseSuccess<RegisteredRepository>(response);
  return payload.data;
}

export async function getRegisteredRepositories({
  baseUrl,
  fetcher,
  getSession,
}: GitHubApiOptions): Promise<RegisteredRepository[]> {
  const client = createApiClient({ baseUrl, fetcher, getSession });
  const response = await client.request("/api/v1/repositories", { authenticated: true });

  if (!response.ok) {
    throw new Error("Registered repositories request failed.");
  }

  const payload = await parseSuccess<RegisteredRepository[]>(response);
  return payload.data;
}

export async function getRegisteredRepository(
  { baseUrl, fetcher, getSession }: GitHubApiOptions,
  repositoryId: string,
): Promise<RegisteredRepository> {
  const client = createApiClient({ baseUrl, fetcher, getSession });
  const response = await client.request(`/api/v1/repositories/${repositoryId}`, {
    authenticated: true,
  });

  if (!response.ok) {
    throw new Error("Registered repository request failed.");
  }

  const payload = await parseSuccess<RegisteredRepository>(response);
  return payload.data;
}

export async function updateRegisteredRepositorySettings(
  { baseUrl, fetcher, getSession }: GitHubApiOptions,
  repositoryId: string,
  settings: UpdateRepositorySettingsInput,
): Promise<RegisteredRepository> {
  const client = createApiClient({ baseUrl, fetcher, getSession });
  const response = await client.request(`/api/v1/repositories/${repositoryId}`, {
    authenticated: true,
    body: JSON.stringify(settings),
    headers: { "Content-Type": "application/json" },
    method: "PATCH",
  });

  if (!response.ok) {
    throw new Error("Repository settings update failed.");
  }

  const payload = await parseSuccess<RegisteredRepository>(response);
  return payload.data;
}

export async function refreshRegisteredRepository(
  { baseUrl, fetcher, getSession }: GitHubApiOptions,
  repositoryId: string,
): Promise<RegisteredRepository> {
  const client = createApiClient({ baseUrl, fetcher, getSession });
  const response = await client.request(`/api/v1/repositories/${repositoryId}/refresh`, {
    authenticated: true,
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Repository refresh failed.");
  }

  const payload = await parseSuccess<RegisteredRepository>(response);
  return payload.data;
}

export async function unregisterRegisteredRepository(
  { baseUrl, fetcher, getSession }: GitHubApiOptions,
  repositoryId: string,
): Promise<void> {
  const client = createApiClient({ baseUrl, fetcher, getSession });
  const response = await client.request(`/api/v1/repositories/${repositoryId}`, {
    authenticated: true,
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Repository unregister failed.");
  }
}
