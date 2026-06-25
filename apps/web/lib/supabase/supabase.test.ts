import { beforeEach, describe, expect, it, vi } from "vitest";

const createClientMock = vi.fn((url: string, anonKey: string) => ({ anonKey, url }));

vi.mock("@supabase/supabase-js", () => ({
  createClient: createClientMock,
}));

describe("Supabase client factories", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    createClientMock.mockClear();
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
      url: "https://example.supabase.co",
    });
    expect(createServerSupabaseClient()).toEqual({
      anonKey: "anon-key",
      url: "https://example.supabase.co",
    });
    expect(createClientMock).toHaveBeenCalledTimes(2);
  });
});
