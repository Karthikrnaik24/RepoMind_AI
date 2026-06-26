// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

const replaceMock = vi.fn();
const { createBrowserSupabaseClientMock } = vi.hoisted(() => ({
  createBrowserSupabaseClientMock: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: replaceMock }),
}));

vi.mock("../../lib/supabase/client", () => ({
  createBrowserSupabaseClient: createBrowserSupabaseClientMock,
}));

import { AuthProvider } from "./auth-provider";
import { useAuth } from "./auth-hooks";

afterEach(() => {
  cleanup();
  createBrowserSupabaseClientMock.mockReset();
  replaceMock.mockReset();
});

function LoadingProbe() {
  const { loading } = useAuth();

  return <div>{loading ? "loading" : "ready"}</div>;
}

function AuthActionsProbe() {
  const { signInWithGoogle, signOut, user } = useAuth();

  return (
    <div>
      <span>{user?.email ?? "signed out"}</span>
      <button type="button" onClick={() => void signInWithGoogle()}>
        Google
      </button>
      <button type="button" onClick={() => void signOut()}>
        Sign out
      </button>
    </div>
  );
}

function createSupabaseMock(session: unknown = null) {
  return {
    auth: {
      getSession: vi.fn(async () => ({ data: { session } })),
      onAuthStateChange: vi.fn(() => ({
        data: { subscription: { unsubscribe: vi.fn() } },
      })),
      signInWithOAuth: vi.fn(async () => ({ data: {}, error: null })),
      signOut: vi.fn(async () => ({ error: null })),
    },
  };
}

describe("AuthProvider", () => {
  it("exposes the initial loading state", () => {
    createBrowserSupabaseClientMock.mockReturnValue({
      auth: {
        getSession: vi.fn(() => new Promise(() => undefined)),
        onAuthStateChange: vi.fn(),
      },
    });

    render(
      <AuthProvider>
        <LoadingProbe />
      </AuthProvider>,
    );

    expect(screen.getByText("loading")).toBeInTheDocument();
  });

  it("starts Google OAuth with the callback redirect", async () => {
    const supabase = createSupabaseMock();
    createBrowserSupabaseClientMock.mockReturnValue(supabase);

    render(
      <AuthProvider>
        <AuthActionsProbe />
      </AuthProvider>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Google" }));

    await waitFor(() => expect(supabase.auth.signInWithOAuth).toHaveBeenCalledOnce());
    expect(supabase.auth.signInWithOAuth).toHaveBeenCalledWith({
      provider: "google",
      options: { redirectTo: "http://localhost:3000/auth/callback" },
    });
  });

  it("clears session state and redirects home on logout", async () => {
    const supabase = createSupabaseMock({
      access_token: "sample-access-token",
      user: { email: "engineer@example.com" },
    });
    createBrowserSupabaseClientMock.mockReturnValue(supabase);

    render(
      <AuthProvider>
        <AuthActionsProbe />
      </AuthProvider>,
    );

    await screen.findByText("engineer@example.com");
    fireEvent.click(screen.getByRole("button", { name: "Sign out" }));

    await waitFor(() => expect(supabase.auth.signOut).toHaveBeenCalledOnce());
    expect(await screen.findByText("signed out")).toBeInTheDocument();
    expect(replaceMock).toHaveBeenCalledWith("/");
  });
});
