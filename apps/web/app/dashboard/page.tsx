"use client";

import React from "react";
import { Suspense, useEffect, useMemo, useState } from "react";
import Image from "next/image";
import { useSearchParams } from "next/navigation";
import type { Session, User } from "@supabase/supabase-js";
import { BadgeCheck, CircleAlert, Github, Globe2, Lock, Search } from "lucide-react";

import {
  getGitHubRepositories,
  type GitHubRepositorySummary,
  type GitHubRepositoryVisibility,
} from "../../api/github";
import { useAuth } from "../../features/auth/auth-hooks";
import { RequireAuth } from "../../features/auth/require-auth";

const githubLinkErrorMessages: Record<string, string> = {
  identity_already_linked: "This GitHub account is already linked.",
  oauth_cancelled: "GitHub linking was cancelled.",
  oauth_failed: "GitHub linking failed. Please try again.",
  provider_unavailable: "GitHub linking is unavailable right now.",
};

function getDisplayName(user: User | null) {
  const fullName = user?.user_metadata?.full_name;
  const name = user?.user_metadata?.name;

  if (typeof fullName === "string" && fullName) {
    return fullName;
  }

  if (typeof name === "string" && name) {
    return name;
  }

  return "Signed-in user";
}

function getAvatarUrl(user: User | null) {
  const avatarUrl = user?.user_metadata?.avatar_url;

  return typeof avatarUrl === "string" && avatarUrl ? avatarUrl : null;
}

function getConnectedProviders(user: User | null) {
  const providers = new Set<string>();
  const primaryProvider = user?.app_metadata?.provider;

  if (typeof primaryProvider === "string" && primaryProvider) {
    providers.add(primaryProvider);
  }

  user?.identities?.forEach((identity) => {
    if (typeof identity.provider === "string" && identity.provider) {
      providers.add(identity.provider);
    }
  });

  return providers;
}

function getProviderMessage(searchParams: URLSearchParams, authError: string | null) {
  if (authError) {
    return authError;
  }

  const githubLinkError = searchParams.get("github_link_error");
  if (!githubLinkError) {
    return null;
  }

  return githubLinkErrorMessages[githubLinkError] ?? githubLinkErrorMessages.oauth_failed;
}

function formatUpdatedAt(value: string | null) {
  if (!value) {
    return "No recent updates";
  }

  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

type ProviderStatusProps = {
  connected: boolean;
  label: string;
};

function ProviderStatus({ connected, label }: ProviderStatusProps) {
  return (
    <div className="flex items-center justify-between rounded-md border border-border bg-background px-4 py-3">
      <div className="flex items-center gap-3">
        <span className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-border bg-secondary text-foreground">
          {label === "GitHub" ? <Github aria-hidden="true" className="h-4 w-4" /> : label.charAt(0)}
        </span>
        <div>
          <p className="text-sm font-medium text-foreground">{label}</p>
          <p className="mt-1 text-xs text-muted-foreground">{connected ? "Connected" : "Not Connected"}</p>
        </div>
      </div>
      {connected ? (
        <span className="inline-flex items-center gap-1 rounded-full border border-primary/30 bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
          <BadgeCheck aria-hidden="true" className="h-3.5 w-3.5" />
          Connected
        </span>
      ) : (
        <span className="rounded-full border border-border bg-secondary px-2 py-1 text-xs font-medium text-muted-foreground">
          Not Connected
        </span>
      )}
    </div>
  );
}

function RepositorySkeletons() {
  return (
    <div className="grid gap-3">
      {Array.from({ length: 3 }).map((_, index) => (
        <div key={index} className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <div className="h-4 w-2/5 animate-pulse rounded bg-muted" />
          <div className="mt-3 h-3 w-3/4 animate-pulse rounded bg-muted" />
          <div className="mt-5 flex gap-2">
            <div className="h-6 w-20 animate-pulse rounded bg-muted" />
            <div className="h-6 w-24 animate-pulse rounded bg-muted" />
          </div>
        </div>
      ))}
    </div>
  );
}

type RepositoryCardProps = {
  repository: GitHubRepositorySummary;
};

function RepositoryCard({ repository }: RepositoryCardProps) {
  return (
    <article className="rounded-lg border border-border bg-card p-4 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-base font-semibold text-card-foreground">{repository.name}</h3>
          <p className="mt-1 text-xs text-muted-foreground">{repository.owner.login}</p>
        </div>
        <span className="inline-flex w-fit items-center gap-1 rounded-full border border-border bg-secondary px-2 py-1 text-xs font-medium text-secondary-foreground">
          {repository.private ? <Lock aria-hidden="true" className="h-3 w-3" /> : <Globe2 aria-hidden="true" className="h-3 w-3" />}
          {repository.visibility ?? (repository.private ? "private" : "public")}
        </span>
      </div>
      <p className="mt-3 text-sm text-muted-foreground">
        {repository.description ?? "No description provided."}
      </p>
      <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        <span className="rounded-md border border-border bg-background px-2 py-1">
          {repository.language ?? "Unknown language"}
        </span>
        <span className="rounded-md border border-border bg-background px-2 py-1">
          Default: {repository.default_branch}
        </span>
        <span className="rounded-md border border-border bg-background px-2 py-1">
          Updated {formatUpdatedAt(repository.updated_at)}
        </span>
      </div>
    </article>
  );
}

type RepositoryBrowserProps = {
  isGitHubConnected: boolean;
  session: Session | null;
};

function RepositoryBrowser({ isGitHubConnected, session }: RepositoryBrowserProps) {
  const [repositories, setRepositories] = useState<GitHubRepositorySummary[]>([]);
  const [search, setSearch] = useState("");
  const [visibility, setVisibility] = useState<GitHubRepositoryVisibility>("all");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canGoNext = repositories.length >= 12;

  useEffect(() => {
    if (!session || !isGitHubConnected) {
      setRepositories([]);
      return;
    }

    let isMounted = true;
    async function loadRepositories(currentSession: Session) {
      setLoading(true);
      setError(null);
      try {
        const result = await getGitHubRepositories(
          { getSession: async () => currentSession },
          { page, perPage: 12, search, visibility },
        );
        if (isMounted) {
          setRepositories(result.data);
        }
      } catch {
        if (isMounted) {
          setRepositories([]);
          setError("Repository discovery is unavailable right now.");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    void loadRepositories(session);

    return () => {
      isMounted = false;
    };
  }, [isGitHubConnected, page, search, session, visibility]);

  const emptyMessage = useMemo(() => {
    if (!isGitHubConnected) {
      return "Connect GitHub to browse repositories.";
    }
    if (search || visibility !== "all") {
      return "No repositories match the current search or filter.";
    }
    return "No repositories were found for this GitHub account.";
  }, [isGitHubConnected, search, visibility]);

  return (
    <section className="pb-8">
      <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-card-foreground">Repositories</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Browse linked GitHub repositories before registration and indexing are enabled.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <label className="relative block">
              <span className="sr-only">Search repositories</span>
              <Search aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                value={search}
                onChange={(event) => {
                  setPage(1);
                  setSearch(event.target.value);
                }}
                placeholder="Search repositories"
                className="h-10 w-full rounded-md border border-border bg-background pl-9 pr-3 text-sm outline-none transition-colors placeholder:text-muted-foreground focus:border-primary sm:w-64"
              />
            </label>
            <label>
              <span className="sr-only">Visibility filter</span>
              <select
                value={visibility}
                onChange={(event) => {
                  setPage(1);
                  setVisibility(event.target.value as GitHubRepositoryVisibility);
                }}
                className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none transition-colors focus:border-primary"
              >
                <option value="all">All</option>
                <option value="public">Public</option>
                <option value="private">Private</option>
              </select>
            </label>
          </div>
        </div>

        {error ? (
          <p className="mt-4 inline-flex items-center gap-2 rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            <CircleAlert aria-hidden="true" className="h-4 w-4" />
            {error}
          </p>
        ) : null}

        <div className="mt-5">
          {loading ? <RepositorySkeletons /> : null}
          {!loading && repositories.length > 0 ? (
            <div className="grid gap-3">
              {repositories.map((repository) => (
                <RepositoryCard key={repository.id} repository={repository} />
              ))}
            </div>
          ) : null}
          {!loading && repositories.length === 0 ? (
            <div className="rounded-lg border border-dashed border-border bg-background p-8 text-center">
              <Github aria-hidden="true" className="mx-auto h-8 w-8 text-muted-foreground" />
              <h3 className="mt-4 text-base font-semibold text-foreground">No repositories to show</h3>
              <p className="mt-2 text-sm text-muted-foreground">{emptyMessage}</p>
            </div>
          ) : null}
        </div>

        <div className="mt-5 flex items-center justify-between border-t border-border pt-4 text-sm">
          <span className="text-muted-foreground">Page {page}</span>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={page === 1 || loading}
              onClick={() => setPage((currentPage) => Math.max(1, currentPage - 1))}
              className="h-9 rounded-md border border-border px-3 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50"
            >
              Previous
            </button>
            <button
              type="button"
              disabled={!canGoNext || loading}
              onClick={() => setPage((currentPage) => currentPage + 1)}
              className="h-9 rounded-md border border-border px-3 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

function DashboardContent() {
  const { authError, linkGitHubIdentity, refreshSession, session, signOut, user } = useAuth();
  const searchParams = useSearchParams();
  const avatarUrl = getAvatarUrl(user);
  const displayName = getDisplayName(user);
  const connectedProviders = getConnectedProviders(user);
  const isGoogleConnected = connectedProviders.has("google");
  const isGitHubConnected = connectedProviders.has("github");
  const providerMessage = getProviderMessage(searchParams, authError);

  useEffect(() => {
    void refreshSession();
  }, [refreshSession]);

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-background px-6 py-10 text-foreground">
      <section className="mx-auto max-w-4xl">
        <p className="text-sm font-medium uppercase text-muted-foreground">Dashboard</p>
        <div className="mt-4 flex flex-col gap-5 border-b border-border pb-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            {avatarUrl ? (
              <Image
                src={avatarUrl}
                alt="User avatar"
                width={56}
                height={56}
                unoptimized
                className="h-14 w-14 rounded-full border border-border object-cover"
              />
            ) : (
              <div className="flex h-14 w-14 items-center justify-center rounded-full border border-border bg-secondary text-lg font-semibold text-secondary-foreground">
                {displayName.charAt(0).toUpperCase()}
              </div>
            )}
            <div>
              <h1 className="text-3xl font-semibold">{displayName}</h1>
              <p className="mt-2 text-sm text-muted-foreground">{user?.email ?? "unknown user"}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => void signOut()}
            className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Log out
          </button>
        </div>

        <section className="py-8">
          <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold text-card-foreground">Authentication Status</h2>
                <p className="mt-2 text-sm text-muted-foreground">
                  Link provider identities to the same RepoMind AI account.
                </p>
              </div>
              {!isGitHubConnected ? (
                <button
                  type="button"
                  onClick={() => void linkGitHubIdentity()}
                  className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                >
                  <Github aria-hidden="true" className="h-4 w-4" />
                  Connect GitHub
                </button>
              ) : null}
            </div>

            {providerMessage ? (
              <p className="mt-4 inline-flex items-center gap-2 rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                <CircleAlert aria-hidden="true" className="h-4 w-4" />
                {providerMessage}
              </p>
            ) : null}

            <div className="mt-5 grid gap-3">
              <ProviderStatus connected={isGoogleConnected} label="Google" />
              <ProviderStatus connected={isGitHubConnected} label="GitHub" />
            </div>
          </div>
        </section>

        <RepositoryBrowser isGitHubConnected={isGitHubConnected} session={session} />
      </section>
    </main>
  );
}

export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-background px-6 text-sm text-muted-foreground">
          Loading dashboard...
        </main>
      }
    >
      <RequireAuth>
        <DashboardContent />
      </RequireAuth>
    </Suspense>
  );
}