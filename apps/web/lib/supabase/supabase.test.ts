import { beforeEach, describe, expect, it, vi } from "vitest";

type CookieOptions = Record<string, unknown>;

type ServerCookieAdapter = {
  get(name: string): string | undefined;
  set(name: string, value: string, options: CookieOptions): void;
  remove(name: string, options: CookieOptions): void;
};

const { createBrowserClientMock, createServerClientMock, cookieStoreMock } = vi.hoisted(() => {
  const cookieStoreMock = {
    get: vi.fn(),
    set: vi.fn(),
  };

  return {
    createBrowserClientMock: vi.fn((url: string, anonKey: string) => ({
      anonKey,
      type: "browser",
      url,
    })),
    createServerClientMock: vi.fn((url: string, anonKey: string, options: unknown) => ({
      anonKey,
      options,
      type: "server",
      url,
    })),
    cookieStoreMock,
  };
});

vi.mock("@supabase/ssr", () => ({
  createBrowserClient: createBrowserClientMock,
  createServerClient: createServerClientMock,
}));

vi.mock("next/headers", () => ({
  cookies: vi.fn(async () => cookieStoreMock),
}));

describe("Supabase client factories", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    createBrowserClientMock.mockClear();
    createServerClientMock.mockClear();
    cookieStoreMock.get.mockReset();
    cookieStoreMock.set.mockReset();
    cookieStoreMock.get.mockReturnValue({ value: "cookie-value" });
    process.env = { ...originalEnv };
    delete process.env.NEXT_PUBLIC_SUPABASE_URL;
    delete process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  });

  it("does not require Supabase env vars at import time", async () => {
    await expect(import("./client")).resolves.toBeDefined();
    await expect(import("./server")).resolves.toBeDefined();
  });

  it("validates browser client env vars inside the factory", async () => {
    const { createBrowserSupabaseClient } = await import("./client");

    expect(() => createBrowserSupabaseClient()).toThrow(
      "Supabase public environment variables are not configured.",
    );
  });

  it("creates browser and server clients from public env vars", async () => {
    process.env.NEXT_PUBLIC_SUPABASE_URL = "https://example.supabase.co";
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY = "anon-key";

    const { createBrowserSupabaseClient } = await import("./client");
    const { createServerSupabaseClient } = await import("./server");

    expect(createBrowserSupabaseClient()).toEqual({
      anonKey: "anon-key",
      type: "browser",
      url: "https://example.supabase.co",
    });
    expect(await createServerSupabaseClient()).toEqual({
      anonKey: "anon-key",
      options: expect.any(Object),
      type: "server",
      url: "https://example.supabase.co",
    });
    expect(createBrowserClientMock).toHaveBeenCalledTimes(1);
    expect(createServerClientMock).toHaveBeenCalledTimes(1);
  });

  it("wires the server client to Next.js cookies for OAuth session persistence", async () => {
    process.env.NEXT_PUBLIC_SUPABASE_URL = "https://example.supabase.co";
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY = "anon-key";

    const { createServerSupabaseClient } = await import("./server");

    await createServerSupabaseClient();

    const [, , options] = createServerClientMock.mock.calls[0] as [
      string,
      string,
      { cookies: ServerCookieAdapter },
    ];

    expect(options.cookies.get("sb-session")).toBe("cookie-value");

    options.cookies.set("sb-session", "next-cookie-value", { path: "/" });
    expect(cookieStoreMock.set).toHaveBeenCalledWith({
      name: "sb-session",
      path: "/",
      value: "next-cookie-value",
    });

    options.cookies.remove("sb-session", { path: "/" });
    expect(cookieStoreMock.set).toHaveBeenCalledWith({
      maxAge: 0,
      name: "sb-session",
      path: "/",
      value: "",
    });
  });
});
