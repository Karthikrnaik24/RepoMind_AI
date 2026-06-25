// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const { createBrowserSupabaseClientMock } = vi.hoisted(() => ({
  createBrowserSupabaseClientMock: vi.fn(),
}));

vi.mock("../../lib/supabase/client", () => ({
  createBrowserSupabaseClient: createBrowserSupabaseClientMock,
}));

import { AuthProvider } from "./auth-provider";
import { useAuth } from "./auth-hooks";

function LoadingProbe() {
  const { loading } = useAuth();

  return <div>{loading ? "loading" : "ready"}</div>;
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
});
