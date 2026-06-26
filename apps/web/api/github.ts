import type { Session } from "@supabase/supabase-js";

import { createApiClient } from "./client";

export type GitHubTokenDebugStatus = {
  github_linked: boolean;
  token_available: boolean;
  provider: "github";
};

type ApiSuccessEnvelope<T> = {
  success: true;
  data: T;
  meta: Record<string, unknown>;
};

type GitHubDebugOptions = {
  baseUrl?: string;
  fetcher?: typeof fetch;
  getSession: () => Promise<Session | null>;
};

export async function getGitHubTokenDebugStatus({
  baseUrl,
  fetcher,
  getSession,
}: GitHubDebugOptions): Promise<GitHubTokenDebugStatus> {
  const client = createApiClient({ baseUrl, fetcher, getSession });
  const response = await client.request("/api/v1/github/debug-token", { authenticated: true });

  if (!response.ok) {
    throw new Error("GitHub token debug request failed.");
  }

  const payload = (await response.json()) as ApiSuccessEnvelope<GitHubTokenDebugStatus>;
  return payload.data;
}