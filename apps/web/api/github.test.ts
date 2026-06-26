import type { Session } from "@supabase/supabase-js";
import { describe, expect, it, vi } from "vitest";

import { getGitHubTokenDebugStatus } from "./github";

describe("getGitHubTokenDebugStatus", () => {
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