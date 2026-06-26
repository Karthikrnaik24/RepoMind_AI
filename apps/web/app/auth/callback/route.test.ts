import { NextRequest } from "next/server";
import { describe, expect, it, vi } from "vitest";

const { createServerSupabaseClientMock } = vi.hoisted(() => ({
  createServerSupabaseClientMock: vi.fn(),
}));

vi.mock("../../../lib/supabase/server", () => ({
  createServerSupabaseClient: createServerSupabaseClientMock,
}));

import { GET } from "./route";

describe("GET /auth/callback", () => {
  it("exchanges the code, restores the session, and redirects to dashboard", async () => {
    createServerSupabaseClientMock.mockReturnValue({
      auth: {
        exchangeCodeForSession: vi.fn(async () => ({ error: null })),
        getSession: vi.fn(async () => ({ data: { session: { access_token: "sample" } } })),
      },
    });

    const response = await GET(new NextRequest("http://localhost:3000/auth/callback?code=sample-code"));

    expect(response.headers.get("location")).toBe("http://localhost:3000/dashboard");
  });

  it("redirects failures to login", async () => {
    createServerSupabaseClientMock.mockReturnValue({
      auth: {
        exchangeCodeForSession: vi.fn(async () => ({ error: new Error("failed") })),
        getSession: vi.fn(),
      },
    });

    const response = await GET(new NextRequest("http://localhost:3000/auth/callback?code=bad-code"));

    expect(response.headers.get("location")).toBe(
      "http://localhost:3000/login?error=authentication_failed",
    );
  });
});
