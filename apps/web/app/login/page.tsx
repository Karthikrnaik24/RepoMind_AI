"use client";

import React from "react";
import { Suspense } from "react";
import { useSearchParams } from "next/navigation";

import { useAuth } from "../../features/auth/auth-hooks";

function LoginContent() {
  const { signInWithGoogle } = useAuth();
  const searchParams = useSearchParams();
  const hasAuthError = searchParams.get("error") === "authentication_failed";

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 text-foreground">
      <section className="w-full max-w-md rounded-lg border border-border bg-card p-8 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-muted-foreground">RepoMind AI</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight">Sign in to understand your repositories</h1>
        {hasAuthError ? (
          <p className="mt-4 rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            Authentication failed. Please try signing in again.
          </p>
        ) : null}
        <div className="mt-8 grid gap-3">
          <button
            type="button"
            onClick={() => void signInWithGoogle()}
            className="h-11 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Continue with Google
          </button>
          <button
            type="button"
            disabled
            className="h-11 rounded-md border border-border bg-secondary px-4 text-sm font-medium text-muted-foreground opacity-70"
          >
            Continue with GitHub
          </button>
        </div>
        <p className="mt-5 text-sm leading-6 text-muted-foreground">
          GitHub OAuth will be enabled in a later sprint.
        </p>
      </section>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center bg-background px-6 text-sm text-muted-foreground">
          Loading sign in...
        </main>
      }
    >
      <LoginContent />
    </Suspense>
  );
}
