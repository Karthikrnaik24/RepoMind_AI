import type { Session } from "@supabase/supabase-js";
import { describe, expect, it, vi } from "vitest";

import { createApiClient } from "./client";

describe("createApiClient", () => {
  it("attaches Authorization header when an access token exists", async () => {
    const fetcherMock = vi.fn(async () => Promise.resolve(new Response(null, { status: 200 })));
    const client = createApiClient({
      baseUrl: "http://api.test",
      fetcher: fetcherMock as unknown as typeof fetch,
      getSession: async () => ({ access_token: "sample-access-token" }) as Session,
    });

    await client.request("/api/v1/me", { authenticated: true });

    const [, init] = fetcherMock.mock.calls[0] as unknown as [RequestInfo | URL, RequestInit];
    expect((init.headers as Headers).get("Authorization")).toBe("Bearer sample-access-token");
  });
});

