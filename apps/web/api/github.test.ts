import type { Session } from "@supabase/supabase-js";
import { describe, expect, it, vi } from "vitest";

import {
  getGitHubRepositories,
  getRegisteredRepositories,
  getRegisteredRepository,
  GitHubRepositoryDiscoveryError,
  refreshRegisteredRepository,
  registerGitHubRepository,
  unregisterRegisteredRepository,
  updateRegisteredRepositorySettings,
} from "./github";

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
  description: null,
  html_url: "https://github.com/Karthikrnaik24/RepoMind_AI",
  registered_at: "2026-06-26T10:00:00Z",
  sync_status: "PENDING",
  last_synced_at: null,
  github_updated_at: "2026-06-26T11:00:00Z",
  created_at: "2026-06-26T10:00:00Z",
  updated_at: "2026-06-26T10:00:00Z",
};

describe("GitHub API helpers", () => {
  it("requests repositories with pagination, search, and visibility filters", async () => {
    const fetcherMock = vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            success: true,
            data: [],
            meta: { page: 2, per_page: 12, count: 0 },
          }),
          { status: 200 },
        ),
    );

    await getGitHubRepositories(
      {
        baseUrl: "http://api.test",
        fetcher: fetcherMock as unknown as typeof fetch,
        getSession: async () =>
          ({
            access_token: "sample-access-token",
            provider_token: "secret-provider-token",
          }) as Session,
      },
      { page: 2, perPage: 12, search: "RepoMind", visibility: "private" },
    );

    const [url, init] = fetcherMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toContain("/api/v1/github/repositories?");
    expect(url).toContain("page=2");
    expect(url).toContain("per_page=12");
    expect(url).toContain("search=RepoMind");
    expect(url).toContain("visibility=private");
    expect((init.headers as Headers).get("Authorization")).toBe("Bearer sample-access-token");
    expect((init.headers as Headers).get("X-GitHub-Provider-Token")).toBe(
      "secret-provider-token",
    );
    expect(url).not.toContain("secret-provider-token");
  });

  it("registers a GitHub repository through the protected repositories API", async () => {
    const fetcherMock = vi.fn(
      async () =>
        new Response(
          JSON.stringify({ success: true, data: registeredRepository, meta: {} }),
          { status: 201 },
        ),
    );

    const repository = await registerGitHubRepository(
      {
        baseUrl: "http://api.test",
        fetcher: fetcherMock as unknown as typeof fetch,
        getSession: async () =>
          ({
            access_token: "sample-access-token",
            provider_token: "secret-provider-token",
          }) as Session,
      },
      {
        github_repository_id: "123",
        full_name: "Karthikrnaik24/RepoMind_AI",
        default_branch: "main",
      },
    );

    const [url, init] = fetcherMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://api.test/api/v1/repositories/register");
    expect(init.method).toBe("POST");
    expect((init.headers as Headers).get("Authorization")).toBe("Bearer sample-access-token");

    expect(JSON.parse(init.body as string)).toEqual({
      github_repository_id: "123",
      full_name: "Karthikrnaik24/RepoMind_AI",
      default_branch: "main",
    });
    expect(repository.sync_status).toBe("PENDING");
  });

  it("fetches registered repositories through the protected repositories API", async () => {
    const fetcherMock = vi.fn(
      async () =>
        new Response(
          JSON.stringify({ success: true, data: [registeredRepository], meta: { count: 1 } }),
          { status: 200 },
        ),
    );

    const repositories = await getRegisteredRepositories({
      baseUrl: "http://api.test",
      fetcher: fetcherMock as unknown as typeof fetch,
      getSession: async () => ({ access_token: "sample-access-token" }) as Session,
    });

    const [url, init] = fetcherMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://api.test/api/v1/repositories");
    expect((init.headers as Headers).get("Authorization")).toBe("Bearer sample-access-token");

    expect(repositories).toHaveLength(1);
    expect(repositories[0].github_repository_id).toBe("123");
  });

  it("fetches a registered repository dashboard payload", async () => {
    const fetcherMock = vi.fn(
      async () =>
        new Response(JSON.stringify({ success: true, data: registeredRepository, meta: {} }), {
          status: 200,
        }),
    );

    const repository = await getRegisteredRepository(
      {
        baseUrl: "http://api.test",
        fetcher: fetcherMock as unknown as typeof fetch,
        getSession: async () =>
          ({
            access_token: "sample-access-token",
            provider_token: "secret-provider-token",
          }) as Session,
      },
      "local-repository-id",
    );

    const [url, init] = fetcherMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://api.test/api/v1/repositories/local-repository-id");
    expect((init.headers as Headers).get("Authorization")).toBe("Bearer sample-access-token");

    expect(repository.name).toBe("RepoMind_AI");
  });

  it("updates repository settings", async () => {
    const fetcherMock = vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            success: true,
            data: { ...registeredRepository, display_name: "Production", favorite: true },
            meta: {},
          }),
          { status: 200 },
        ),
    );

    const repository = await updateRegisteredRepositorySettings(
      {
        baseUrl: "http://api.test",
        fetcher: fetcherMock as unknown as typeof fetch,
        getSession: async () =>
          ({
            access_token: "sample-access-token",
            provider_token: "secret-provider-token",
          }) as Session,
      },
      "local-repository-id",
      { display_name: "Production", favorite: true, notes: null },
    );

    const [url, init] = fetcherMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://api.test/api/v1/repositories/local-repository-id");
    expect(init.method).toBe("PATCH");
    expect(JSON.parse(init.body as string)).toEqual({
      display_name: "Production",
      favorite: true,
      notes: null,
    });
    expect(repository.favorite).toBe(true);
  });

  it("refreshes repository metadata", async () => {
    const fetcherMock = vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            success: true,
            data: { ...registeredRepository, sync_status: "READY", last_synced_at: "2026-06-27T10:00:00Z" },
            meta: {},
          }),
          { status: 200 },
        ),
    );

    const repository = await refreshRegisteredRepository(
      {
        baseUrl: "http://api.test",
        fetcher: fetcherMock as unknown as typeof fetch,
        getSession: async () =>
          ({
            access_token: "sample-access-token",
            provider_token: "secret-provider-token",
          }) as Session,
      },
      "local-repository-id",
    );

    const [url, init] = fetcherMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://api.test/api/v1/repositories/local-repository-id/refresh");
    expect(init.method).toBe("POST");
    expect(repository.sync_status).toBe("READY");
  });

  it("unregisters a repository without serializing secrets", async () => {
    const fetcherMock = vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            success: true,
            data: { id: "local-repository-id", removed: true },
            meta: {},
          }),
          { status: 200 },
        ),
    );

    await unregisterRegisteredRepository(
      {
        baseUrl: "http://api.test",
        fetcher: fetcherMock as unknown as typeof fetch,
        getSession: async () =>
          ({
            access_token: "sample-access-token",
            provider_token: "secret-provider-token",
          }) as Session,
      },
      "local-repository-id",
    );

    const [url, init] = fetcherMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://api.test/api/v1/repositories/local-repository-id");
    expect(init.method).toBe("DELETE");
    expect(JSON.stringify(init)).not.toContain("secret-provider-token");
  });

  it("maps rate limit responses to typed repository discovery errors", async () => {
    const fetcherMock = vi.fn(async () => new Response(null, { status: 429 }));

    await expect(
      getGitHubRepositories({
        baseUrl: "http://api.test",
        fetcher: fetcherMock as unknown as typeof fetch,
        getSession: async () =>
          ({
            access_token: "sample-access-token",
            provider_token: "secret-provider-token",
          }) as Session,
      }),
    ).rejects.toMatchObject(new GitHubRepositoryDiscoveryError("rate_limited"));
  });

  it("maps missing GitHub provider token responses to reconnect-required errors", async () => {
    const fetcherMock = vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            success: false,
            error: {
              code: "github_reconnect_required",
              message: "Reconnect GitHub to refresh repository access.",
            },
          }),
          { status: 401 },
        ),
    );

    await expect(
      getGitHubRepositories({
        baseUrl: "http://api.test",
        fetcher: fetcherMock as unknown as typeof fetch,
        getSession: async () => ({ access_token: "sample-access-token" }) as Session,
      }),
    ).rejects.toMatchObject(new GitHubRepositoryDiscoveryError("reconnect_required"));

    const [, init] = fetcherMock.mock.calls[0] as unknown as [string, RequestInit];
    expect((init.headers as Headers).get("X-GitHub-Provider-Token")).toBeNull();
    expect(JSON.stringify(init)).not.toContain("secret-provider-token");
  });

});



