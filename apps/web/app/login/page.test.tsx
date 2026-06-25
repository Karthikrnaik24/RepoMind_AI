// @vitest-environment jsdom

import React from "react";
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import LoginPage from "./page";

describe("LoginPage", () => {
  it("renders disabled OAuth placeholders", () => {
    render(<LoginPage />);

    expect(screen.getByText("RepoMind AI")).toBeInTheDocument();
    expect(screen.getByText("Sign in to understand your repositories")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Continue with Google" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Continue with GitHub" })).toBeDisabled();
    expect(screen.getByText("OAuth providers will be enabled in the next sprint.")).toBeInTheDocument();
  });
});
