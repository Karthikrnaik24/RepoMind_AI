import React from "react";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 text-foreground">
      <section className="w-full max-w-md rounded-lg border border-border bg-card p-8 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-muted-foreground">RepoMind AI</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight">Sign in to understand your repositories</h1>
        <div className="mt-8 grid gap-3">
          <button
            type="button"
            disabled
            className="h-11 rounded-md border border-border bg-secondary px-4 text-sm font-medium text-muted-foreground opacity-70"
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
          OAuth providers will be enabled in the next sprint.
        </p>
      </section>
    </main>
  );
}
