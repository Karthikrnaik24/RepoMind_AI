import { NextRequest } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { createServerSupabaseClientMock } = vi.hoisted(() => ({
  createServerSupabaseClientMock: vi.fn(),
}));

vi.mock("../../../lib/supabase/server", () => ({
  createServerSupabaseClient: createServerSupabaseClientMock,
}));

import { GET } from "./route";

describe("GET /auth/callback", () => {
  beforeEach(() => {
    createServerSupabaseClientMock.mockReset();
  });

  it("uses the cookie-aware server client, exchanges the code, and redirects to dashboard", async () => {
    const exchangeCodeForSessionMock = vi.fn(async () => ({ error: null }));
    const getSessionMock = vi.fn(async () => ({ data: { session: { access_token: "sample" } } }));
    createServerSupabaseClientMock.mockResolvedValue({
      auth: {
        exchangeCodeForSession: exchangeCodeForSessionMock,
        getSession: getSessionMock,
      },
    });

    const response = await GET(
      new NextRequest("http://localhost:3000/auth/callback?code=sample-code"),
    );

    expect(createServerSupabaseClientMock).toHaveBeenCalledOnce();
    expect(exchangeCodeForSessionMock).toHaveBeenCalledWith("sample-code");
    expect(getSessionMock).toHaveBeenCalledOnce();
    expect(response.headers.get("location")).toBe("http://localhost:3000/dashboard");
  });

  it("redirects callback exchange failures to login when no session exists", async () => {
    createServerSupabaseClientMock.mockResolvedValue({
      auth: {
        exchangeCodeForSession: vi.fn(async () => ({ error: new Error("failed") })),
        getSession: vi.fn(async () => ({ data: { session: null } })),
      },
    });

    const response = await GET(
      new NextRequest("http://localhost:3000/auth/callback?code=bad-code"),
    );

    expect(response.headers.get("location")).toBe(
      "http://localhost:3000/login?error=authentication_failed",
    );
  });

  it("redirects link failures to dashboard when the existing session survives", async () => {
    createServerSupabaseClientMock.mockResolvedValue({
      auth: {
        exchangeCodeForSession: vi.fn(),
        getSession: vi.fn(async () => ({ data: { session: { access_token: "sample" } } })),
      },
    });

    const response = await GET(
      new NextRequest("http://localhost:3000/auth/callback?error=access_denied"),
    );

    expect(response.headers.get("location")).toBe(
      "http://localhost:3000/dashboard?github_link_error=oauth_cancelled",
    );
  });

  it("redirects missing restored sessions to login", async () => {
    createServerSupabaseClientMock.mockResolvedValue({
      auth: {
        exchangeCodeForSession: vi.fn(async () => ({ error: null })),
        getSession: vi.fn(async () => ({ data: { session: null } })),
      },
    });

    const response = await GET(
      new NextRequest("http://localhost:3000/auth/callback?code=sample-code"),
    );

    expect(response.headers.get("location")).toBe(
      "http://localhost:3000/login?error=authentication_failed",
    );
  });

  it("redirects unexpected callback errors to login without exposing internals", async () => {
    createServerSupabaseClientMock.mockRejectedValue(new Error("cookie failure"));

    const response = await GET(
      new NextRequest("http://localhost:3000/auth/callback?code=sample-code"),
    );

    expect(response.headers.get("location")).toBe(
      "http://localhost:3000/login?error=authentication_failed",
    );
  });
});
