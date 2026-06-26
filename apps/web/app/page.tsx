"use client";

import Link from "next/link";

import { useAuth } from "../features/auth/auth-hooks";

export default function HomePage() {
  const { loading, session, signOut } = useAuth();
  const isAuthenticated = Boolean(session);

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 text-foreground">
      <section className="mx-auto max-w-3xl text-center">
        <p className="mb-4 text-sm font-medium uppercase tracking-wide text-muted-foreground">
          Repository Intelligence
        </p>
        <h1 className="text-4xl font-semibold tracking-tight sm:text-6xl">RepoMind AI</h1>
        <p className="mt-6 text-lg leading-8 text-muted-foreground sm:text-xl">
          AI Software Engineer for GitHub Repositories
        </p>
        <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
          {!loading && !isAuthenticated ? (
            <Link
              href="/login"
              className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              Sign in
            </Link>
          ) : null}
          <Link
            href="/dashboard"
            className="inline-flex h-10 items-center justify-center rounded-md border border-border bg-background px-5 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
          >
            Dashboard
          </Link>
          {!loading && isAuthenticated ? (
            <button
              type="button"
              onClick={() => void signOut()}
              className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              Logout
            </button>
          ) : null}
        </div>
      </section>
    </main>
  );
}
