// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const replaceMock = vi.fn();
const useAuthMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: replaceMock }),
}));

vi.mock("./auth-hooks", () => ({
  useAuth: () => useAuthMock(),
}));

import { RequireAuth } from "./require-auth";

describe("RequireAuth", () => {
  it("shows a loading state while auth is resolving", () => {
    useAuthMock.mockReturnValue({ loading: true, session: null });

    render(
      <RequireAuth>
        <div>Protected</div>
      </RequireAuth>,
    );

    expect(screen.getByText("Loading session...")).toBeInTheDocument();
  });

  it("redirects unauthenticated users to login", async () => {
    useAuthMock.mockReturnValue({ loading: false, session: null });

    render(
      <RequireAuth>
        <div>Protected</div>
      </RequireAuth>,
    );

    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith("/login"));
    expect(screen.queryByText("Protected")).not.toBeInTheDocument();
  });

  it("renders children when a session exists", () => {
    useAuthMock.mockReturnValue({ loading: false, session: { access_token: "sample" } });

    render(
      <RequireAuth>
        <div>Protected</div>
      </RequireAuth>,
    );

    expect(screen.getByText("Protected")).toBeInTheDocument();
  });
});
