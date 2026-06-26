"use client";

import React from "react";
import { useEffect, useState } from "react";
import Link from "next/link";
import { CircleAlert, GitBranch, Github, RefreshCw } from "lucide-react";

import { getRegisteredRepositories, type RegisteredRepository } from "../../api/github";
import { useAuth } from "../../features/auth/auth-hooks";
import { RequireAuth } from "../../features/auth/require-auth";

function RegisteredRepositorySkeletons() {
  return (
    <div className="grid gap-3" aria-label="Loading registered repositories">
      {Array.from({ length: 3 }).map((_, index) => (
        <div key={index} className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              <div className="h-4 w-2/5 animate-pulse rounded bg-muted" />
              <div className="mt-2 h-3 w-1/4 animate-pulse rounded bg-muted" />
            </div>
            <div className="h-6 w-24 animate-pulse rounded-full bg-muted" />
          </div>
          <div className="mt-4 h-3 w-full animate-pulse rounded bg-muted" />
          <div className="mt-2 h-3 w-2/3 animate-pulse rounded bg-muted" />
        </div>
      ))}
    </div>
  );
}

function formatRegisteredAt(value: string) {
  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function RegisteredRepositoryCard({ repository }: { repository: RegisteredRepository }) {
  return (
    <article className="rounded-lg border border-border bg-card p-4 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h2 className="truncate text-base font-semibold text-card-foreground">
            {repository.name}
          </h2>
          <p className="mt-1 truncate text-sm text-muted-foreground">{repository.full_name}</p>
        </div>
        <span className="inline-flex w-fit rounded-full border border-primary/30 bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
          {repository.sync_status}
        </span>
      </div>

      <p className="mt-4 text-sm text-muted-foreground">
        {repository.description || "No description provided for this repository."}
      </p>

      <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        <span className="rounded-md border border-border bg-background px-2 py-1 font-medium text-foreground">
          {repository.language ?? "Unknown language"}
        </span>
        <span className="inline-flex items-center gap-1 rounded-md border border-border bg-background px-2 py-1">
          <GitBranch aria-hidden="true" className="h-3 w-3" />
          {repository.default_branch}
        </span>
        <span className="rounded-md border border-border bg-background px-2 py-1 capitalize">
          {repository.visibility}
        </span>
        <span className="rounded-md border border-border bg-background px-2 py-1">
          Registered {formatRegisteredAt(repository.registered_at)}
        </span>
      </div>
    </article>
  );
}

function RepositoriesContent() {
  const { session } = useAuth();
  const [repositories, setRepositories] = useState<RegisteredRepository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryAttempt, setRetryAttempt] = useState(0);

  useEffect(() => {
    if (!session) {
      return;
    }

    let isMounted = true;
    async function loadRepositories() {
      setLoading(true);
      setError(null);
      try {
        const result = await getRegisteredRepositories({ getSession: async () => session });
        if (isMounted) {
          setRepositories(result);
        }
      } catch {
        if (isMounted) {
          setRepositories([]);
          setError("Registered repositories could not be loaded. Please retry.");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    void loadRepositories();

    return () => {
      isMounted = false;
    };
  }, [retryAttempt, session]);

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <section className="mx-auto max-w-4xl">
        <div className="flex flex-col gap-4 border-b border-border pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-medium uppercase text-muted-foreground">My Repositories</p>
            <h1 className="mt-3 text-3xl font-semibold">Registered repositories</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Managed repositories registered from your linked GitHub account.
            </p>
          </div>
          <Link
            href="/dashboard"
            className="inline-flex h-10 w-fit items-center justify-center rounded-md border border-border bg-background px-4 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
          >
            Browse GitHub repositories
          </Link>
        </div>

        <div className="mt-6" aria-live="polite" aria-busy={loading}>
          {loading ? <RegisteredRepositorySkeletons /> : null}

          {!loading && error ? (
            <div
              role="alert"
              className="rounded-md border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive"
            >
              <p className="inline-flex items-center gap-2">
                <CircleAlert aria-hidden="true" className="h-4 w-4" />
                {error}
              </p>
              <button
                type="button"
                onClick={() => setRetryAttempt((currentAttempt) => currentAttempt + 1)}
                className="mt-3 inline-flex h-9 items-center justify-center gap-2 rounded-md border border-destructive/40 bg-background px-3 text-sm font-medium text-foreground outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-destructive/30"
              >
                <RefreshCw aria-hidden="true" className="h-4 w-4" />
                Retry
              </button>
            </div>
          ) : null}

          {!loading && !error && repositories.length > 0 ? (
            <div className="grid gap-3">
              {repositories.map((repository) => (
                <RegisteredRepositoryCard key={repository.id} repository={repository} />
              ))}
            </div>
          ) : null}

          {!loading && !error && repositories.length === 0 ? (
            <div className="rounded-lg border border-dashed border-border bg-card p-8 text-center shadow-sm">
              <Github aria-hidden="true" className="mx-auto h-8 w-8 text-muted-foreground" />
              <h2 className="mt-4 text-base font-semibold text-card-foreground">
                No registered repositories yet
              </h2>
              <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
                Register repositories from the dashboard to make them managed RepoMind AI resources.
              </p>
            </div>
          ) : null}
        </div>
      </section>
    </main>
  );
}

export default function RepositoriesPage() {
  return (
    <RequireAuth>
      <RepositoriesContent />
    </RequireAuth>
  );
}