import type { Session } from "@supabase/supabase-js";
import { describe, expect, it, vi } from "vitest";

import { getGitHubRepositories, getGitHubTokenDebugStatus } from "./github";

describe("GitHub API helpers", () => {
  it("requests the protected debug-token endpoint with the session token", async () => {
    const fetcherMock = vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            success: true,
            data: { github_linked: true, token_available: true, provider: "github" },
            meta: {},
          }),
          { status: 200 },
        ),
    );

    const status = await getGitHubTokenDebugStatus({
      baseUrl: "http://api.test",
      fetcher: fetcherMock as unknown as typeof fetch,
      getSession: async () => ({ access_token: "sample-access-token" }) as Session,
    });

    const [url, init] = fetcherMock.mock.calls[0] as unknown as [RequestInfo | URL, RequestInit];
    expect(url).toBe("http://api.test/api/v1/github/debug-token");
    expect((init.headers as Headers).get("Authorization")).toBe("Bearer sample-access-token");
    expect(status).toEqual({ github_linked: true, token_available: true, provider: "github" });
  });

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
        getSession: async () => ({ access_token: "sample-access-token" }) as Session,
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
  });

  it("does not serialize provider tokens from the API response", async () => {
    const fetcherMock = vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            success: true,
            data: { github_linked: true, token_available: false, provider: "github" },
            meta: {},
          }),
          { status: 200 },
        ),
    );

    const status = await getGitHubTokenDebugStatus({
      baseUrl: "http://api.test",
      fetcher: fetcherMock as unknown as typeof fetch,
      getSession: async () => ({ access_token: "secret-provider-token" }) as Session,
    });

    expect(JSON.stringify(status)).not.toContain("secret-provider-token");
  });
});