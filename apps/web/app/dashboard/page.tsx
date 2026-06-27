"use client";

import React from "react";
import { Suspense, useEffect, useMemo, useState } from "react";
import Image from "next/image";
import { useSearchParams } from "next/navigation";
import type { Session, User } from "@supabase/supabase-js";
import {
  BadgeCheck,
  CircleAlert,
  GitBranch,
  Github,
  Globe2,
  Lock,
  RefreshCw,
  Search,
} from "lucide-react";

import {
  getGitHubRepositories,
  getRegisteredRepositories,
  GitHubRepositoryDiscoveryError,
  registerGitHubRepository,
  type GitHubRepositorySummary,
  type GitHubRepositoryVisibility,
  type RegisteredRepository,
} from "../../api/github";
import { useAuth } from "../../features/auth/auth-hooks";
import { RequireAuth } from "../../features/auth/require-auth";

const githubLinkErrorMessages: Record<string, string> = {
  identity_already_linked: "This GitHub account is already linked.",
  oauth_cancelled: "GitHub connection was cancelled. You can try again whenever you are ready.",
  oauth_failed: "GitHub connection failed. Please try again from the dashboard.",
  provider_unavailable: "GitHub is unavailable right now. Please try again later.",
};

const repositoryDiscoveryErrorMessages = {
  fetch_failed: "Repository fetch failed. Please try again.",
  github_unavailable: "GitHub is unavailable right now. Please retry in a moment.",
  rate_limited: "GitHub rate limit exceeded. Please wait before trying again.",
  token_expired: "Your GitHub session needs to be refreshed. Please sign in again if retry fails.",
};

const repositoryRegistrationErrorMessage =
  "Repository registration failed. Please verify access and retry.";

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
  description: string;
  label: string;
};

function ProviderStatus({ connected, description, label }: ProviderStatusProps) {
  return (
    <article className="flex items-center justify-between gap-4 rounded-lg border border-border bg-background px-4 py-4 shadow-sm">
      <div className="flex min-w-0 items-center gap-3">
        <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-md border border-border bg-secondary text-sm font-semibold text-foreground">
          {label === "GitHub" ? <Github aria-hidden="true" className="h-4 w-4" /> : label.charAt(0)}
        </span>
        <div className="min-w-0">
          <h3 className="text-sm font-semibold text-foreground">{label}</h3>
          <p className="mt-1 text-xs leading-5 text-muted-foreground">{description}</p>
        </div>
      </div>
      {connected ? (
        <span className="inline-flex shrink-0 items-center gap-1 rounded-full border border-primary/30 bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
          <BadgeCheck aria-hidden="true" className="h-3.5 w-3.5" />
          Connected
        </span>
      ) : (
        <span className="shrink-0 rounded-full border border-border bg-secondary px-2 py-1 text-xs font-medium text-muted-foreground">
          Not Connected
        </span>
      )}
    </article>
  );
}

function RepositorySkeletons() {
  return (
    <div className="grid gap-3" aria-label="Loading repositories">
      {Array.from({ length: 3 }).map((_, index) => (
        <div key={index} className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <div className="flex items-start gap-3">
            <div className="h-10 w-10 animate-pulse rounded-full bg-muted" />
            <div className="min-w-0 flex-1">
              <div className="h-4 w-2/5 animate-pulse rounded bg-muted" />
              <div className="mt-2 h-3 w-1/4 animate-pulse rounded bg-muted" />
            </div>
            <div className="h-6 w-20 animate-pulse rounded-full bg-muted" />
          </div>
          <div className="mt-4 h-3 w-full animate-pulse rounded bg-muted" />
          <div className="mt-2 h-3 w-3/5 animate-pulse rounded bg-muted" />
          <div className="mt-5 flex flex-wrap gap-2">
            <div className="h-6 w-24 animate-pulse rounded bg-muted" />
            <div className="h-6 w-28 animate-pulse rounded bg-muted" />
            <div className="h-6 w-32 animate-pulse rounded bg-muted" />
          </div>
        </div>
      ))}
    </div>
  );
}

type RepositoryCardProps = {
  isRegistered: boolean;
  isRegistering: boolean;
  onRegister: (repository: GitHubRepositorySummary) => void;
  repository: GitHubRepositorySummary;
};

function RepositoryCard({
  isRegistered,
  isRegistering,
  onRegister,
  repository,
}: RepositoryCardProps) {
  const visibility = repository.visibility ?? (repository.private ? "private" : "public");

  return (
    <article className="rounded-lg border border-border bg-card p-4 shadow-sm transition-colors hover:border-primary/40">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex min-w-0 items-start gap-3">
          {repository.owner.avatar_url ? (
            <Image
              src={repository.owner.avatar_url}
              alt={`${repository.owner.login} avatar`}
              width={40}
              height={40}
              unoptimized
              className="h-10 w-10 rounded-full border border-border object-cover"
            />
          ) : (
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-border bg-secondary text-sm font-semibold text-secondary-foreground">
              {repository.owner.login.charAt(0).toUpperCase()}
            </div>
          )}
          <div className="min-w-0">
            <h3 className="truncate text-base font-semibold text-card-foreground">
              {repository.name}
            </h3>
            <p className="mt-1 truncate text-xs text-muted-foreground">{repository.owner.login}</p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2 sm:justify-end">
          <span className="inline-flex w-fit items-center gap-1 rounded-full border border-border bg-secondary px-2 py-1 text-xs font-medium capitalize text-secondary-foreground">
            {repository.private ? (
              <Lock aria-hidden="true" className="h-3 w-3" />
            ) : (
              <Globe2 aria-hidden="true" className="h-3 w-3" />
            )}
            {visibility}
          </span>
          {isRegistered ? (
            <span className="inline-flex w-fit items-center gap-1 rounded-full border border-primary/30 bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
              <BadgeCheck aria-hidden="true" className="h-3.5 w-3.5" />
              Registered
            </span>
          ) : null}
        </div>
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
        <span className="rounded-md border border-border bg-background px-2 py-1">
          Updated {formatUpdatedAt(repository.updated_at)}
        </span>
      </div>

      <div className="mt-5 flex justify-end border-t border-border pt-4">
        <button
          type="button"
          disabled={isRegistered || isRegistering}
          onClick={() => onRegister(repository)}
          className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground outline-none transition-colors hover:bg-primary/90 focus:ring-2 focus:ring-primary/30 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isRegistered ? "Registered" : isRegistering ? "Registering..." : "Register Repository"}
        </button>
      </div>
    </article>
  );
}

type RepositoryBrowserProps = {
  isGitHubConnected: boolean;
  session: Session | null;
};

function getRepositoryErrorMessage(error: unknown) {
  if (error instanceof GitHubRepositoryDiscoveryError) {
    return repositoryDiscoveryErrorMessages[error.code];
  }

  return repositoryDiscoveryErrorMessages.fetch_failed;
}

function RepositoryBrowser({ isGitHubConnected, session }: RepositoryBrowserProps) {
  const [repositories, setRepositories] = useState<GitHubRepositorySummary[]>([]);
  const [registeredRepositories, setRegisteredRepositories] = useState<RegisteredRepository[]>([]);
  const [search, setSearch] = useState("");
  const [visibility, setVisibility] = useState<GitHubRepositoryVisibility>("all");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [registrationError, setRegistrationError] = useState<string | null>(null);
  const [registeringIds, setRegisteringIds] = useState<Set<number>>(() => new Set());
  const [retryAttempt, setRetryAttempt] = useState(0);

  const registeredRepositoryIds = useMemo(
    () => new Set(registeredRepositories.map((repository) => repository.github_repository_id)),
    [registeredRepositories],
  );
  const canGoNext = repositories.length >= 12;
  const hasActiveFilter = Boolean(search.trim()) || visibility !== "all";

  useEffect(() => {
    if (!session || !isGitHubConnected) {
      setRepositories([]);
      setRegisteredRepositories([]);
      setError(null);
      return;
    }

    let isMounted = true;
    async function loadRepositories(currentSession: Session) {
      setLoading(true);
      setError(null);
      try {
        const [repositoryResult, registeredResult] = await Promise.all([
          getGitHubRepositories(
            { getSession: async () => currentSession },
            { page, perPage: 12, search, visibility },
          ),
          getRegisteredRepositories({ getSession: async () => currentSession }),
        ]);
        if (isMounted) {
          setRepositories(repositoryResult.data);
          setRegisteredRepositories(registeredResult);
        }
      } catch (caughtError) {
        if (isMounted) {
          setRepositories([]);
          setError(getRepositoryErrorMessage(caughtError));
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
  }, [isGitHubConnected, page, retryAttempt, search, session, visibility]);

  const emptyState = useMemo(() => {
    if (!isGitHubConnected) {
      return {
        title: "Connect GitHub to browse repositories",
        message: "Repository discovery starts after your GitHub identity is linked.",
      };
    }

    if (hasActiveFilter) {
      return {
        title: "Search returned no matches",
        message: "GitHub Search did not return repositories for this name and visibility filter.",
      };
    }

    return {
      title: "GitHub account has no repositories",
      message: "No repositories were returned for this linked GitHub account.",
    };
  }, [hasActiveFilter, isGitHubConnected]);

  async function handleRegister(repository: GitHubRepositorySummary) {
    if (!session || registeredRepositoryIds.has(String(repository.id))) {
      return;
    }

    setRegistrationError(null);
    setRegisteringIds((currentIds) => new Set(currentIds).add(repository.id));
    try {
      const registeredRepository = await registerGitHubRepository(
        { getSession: async () => session },
        {
          github_repository_id: String(repository.id),
          full_name: repository.full_name,
          default_branch: repository.default_branch,
        },
      );
      setRegisteredRepositories((currentRepositories) => [
        ...currentRepositories.filter(
          (currentRepository) => currentRepository.github_repository_id !== String(repository.id),
        ),
        registeredRepository,
      ]);
    } catch {
      setRegistrationError(repositoryRegistrationErrorMessage);
    } finally {
      setRegisteringIds((currentIds) => {
        const nextIds = new Set(currentIds);
        nextIds.delete(repository.id);
        return nextIds;
      });
    }
  }

  return (
    <section className="pb-8" aria-labelledby="repositories-heading">
      <div className="rounded-lg border border-border bg-card p-4 shadow-sm sm:p-5">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div>
            <h2 id="repositories-heading" className="text-lg font-semibold text-card-foreground">
              Repositories
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Browse linked GitHub repositories and register the ones RepoMind AI should manage.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_160px] xl:w-[30rem]">
            <div>
              <label className="relative block" htmlFor="repository-search">
                <span className="sr-only">Search repositories</span>
                <Search
                  aria-hidden="true"
                  className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
                />
                <input
                  id="repository-search"
                  value={search}
                  onChange={(event) => {
                    setPage(1);
                    setSearch(event.target.value);
                  }}
                  placeholder="Search repositories"
                  aria-describedby="repository-search-help"
                  className="h-10 w-full rounded-md border border-border bg-background pl-9 pr-3 text-sm outline-none transition-colors placeholder:text-muted-foreground focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
              </label>
              <p id="repository-search-help" className="mt-2 text-xs text-muted-foreground">
                Searching across repositories with GitHub Search.
              </p>
            </div>
            <label htmlFor="repository-visibility">
              <span className="sr-only">Visibility filter</span>
              <select
                id="repository-visibility"
                value={visibility}
                onChange={(event) => {
                  setPage(1);
                  setVisibility(event.target.value as GitHubRepositoryVisibility);
                }}
                className="h-10 w-full rounded-md border border-border bg-background px-3 text-sm outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/20"
              >
                <option value="all">All</option>
                <option value="public">Public</option>
                <option value="private">Private</option>
              </select>
            </label>
          </div>
        </div>

        {error ? (
          <div
            role="alert"
            className="mt-4 flex flex-col gap-3 rounded-md border border-destructive/40 bg-destructive/10 px-3 py-3 text-sm text-destructive sm:flex-row sm:items-center sm:justify-between"
          >
            <span className="inline-flex items-center gap-2">
              <CircleAlert aria-hidden="true" className="h-4 w-4 shrink-0" />
              {error}
            </span>
            <button
              type="button"
              onClick={() => setRetryAttempt((currentAttempt) => currentAttempt + 1)}
              className="inline-flex h-9 w-fit items-center justify-center gap-2 rounded-md border border-destructive/40 bg-background px-3 text-sm font-medium text-foreground outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-destructive/30"
            >
              <RefreshCw aria-hidden="true" className="h-4 w-4" />
              Retry
            </button>
          </div>
        ) : null}

        {registrationError ? (
          <p
            role="alert"
            className="mt-4 inline-flex items-center gap-2 rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive"
          >
            <CircleAlert aria-hidden="true" className="h-4 w-4" />
            {registrationError}
          </p>
        ) : null}

        <div className="mt-5" aria-live="polite" aria-busy={loading}>
          {loading ? <RepositorySkeletons /> : null}
          {!loading && repositories.length > 0 ? (
            <div className="grid gap-3">
              {repositories.map((repository) => (
                <RepositoryCard
                  key={repository.id}
                  isRegistered={registeredRepositoryIds.has(String(repository.id))}
                  isRegistering={registeringIds.has(repository.id)}
                  onRegister={handleRegister}
                  repository={repository}
                />
              ))}
            </div>
          ) : null}
          {!loading && repositories.length === 0 && !error ? (
            <div className="rounded-lg border border-dashed border-border bg-background p-8 text-center">
              <Github aria-hidden="true" className="mx-auto h-8 w-8 text-muted-foreground" />
              <h3 className="mt-4 text-base font-semibold text-foreground">{emptyState.title}</h3>
              <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
                {emptyState.message}
              </p>
            </div>
          ) : null}
        </div>

        <div className="mt-5 flex flex-col gap-3 border-t border-border pt-4 text-sm sm:flex-row sm:items-center sm:justify-between">
          <span className="text-muted-foreground">Page {page}</span>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={page === 1 || loading}
              onClick={() => setPage((currentPage) => Math.max(1, currentPage - 1))}
              className="h-9 rounded-md border border-border px-3 text-sm font-medium outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-primary/20 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Previous
            </button>
            <button
              type="button"
              disabled={!canGoNext || loading}
              onClick={() => setPage((currentPage) => currentPage + 1)}
              className="h-9 rounded-md border border-border px-3 text-sm font-medium outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-primary/20 disabled:cursor-not-allowed disabled:opacity-50"
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
    <main className="min-h-[calc(100vh-4rem)] bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
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
            className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground outline-none transition-colors hover:bg-primary/90 focus:ring-2 focus:ring-primary/30"
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
                  className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground outline-none transition-colors hover:bg-primary/90 focus:ring-2 focus:ring-primary/30"
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
              <ProviderStatus
                connected={isGoogleConnected}
                description="Primary application sign-in and account recovery."
                label="Google"
              />
              <ProviderStatus
                connected={isGitHubConnected}
                description="Repository discovery and future source access."
                label="GitHub"
              />
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
