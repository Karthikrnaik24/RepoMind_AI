"use client";

import React from "react";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  BadgeCheck,
  Bot,
  CircleAlert,
  Code2,
  ExternalLink,
  GitBranch,
  Globe2,
  Lock,
  RefreshCw,
  Sparkles,
} from "lucide-react";

import { getRegisteredRepository, type RegisteredRepository } from "../../../api/github";
import { useAuth } from "../../../features/auth/auth-hooks";
import { RequireAuth } from "../../../features/auth/require-auth";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function getRepositoryIdParam(value: string | string[] | undefined) {
  if (Array.isArray(value)) {
    return value[0] ?? "";
  }

  return value ?? "";
}

type StatusCardProps = {
  title: string;
  value: string;
  description: string;
  disabled?: boolean;
};

function StatusCard({ description, disabled = false, title, value }: StatusCardProps) {
  return (
    <div
      className={
        disabled
          ? "rounded-lg border border-dashed border-border bg-secondary/50 p-4 opacity-75"
          : "rounded-lg border border-border bg-card p-4 shadow-sm"
      }
    >
      <p className="text-sm font-medium text-muted-foreground">{title}</p>
      <p className="mt-3 text-xl font-semibold text-foreground">{value}</p>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
    </div>
  );
}

function MetadataRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1 border-b border-border py-3 last:border-b-0 sm:flex-row sm:items-center sm:justify-between">
      <dt className="text-sm font-medium text-muted-foreground">{label}</dt>
      <dd className="break-all text-sm text-foreground sm:text-right">{value}</dd>
    </div>
  );
}

function RepositoryDashboardSkeleton() {
  return (
    <main className="min-h-[calc(100vh-4rem)] bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <section className="mx-auto max-w-5xl">
        <div className="h-4 w-40 animate-pulse rounded bg-muted" />
        <div className="mt-5 rounded-lg border border-border bg-card p-5 shadow-sm">
          <div className="h-7 w-64 animate-pulse rounded bg-muted" />
          <div className="mt-3 h-4 w-80 animate-pulse rounded bg-muted" />
        </div>
        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="rounded-lg border border-border bg-card p-4 shadow-sm">
              <div className="h-4 w-28 animate-pulse rounded bg-muted" />
              <div className="mt-4 h-6 w-20 animate-pulse rounded bg-muted" />
              <div className="mt-3 h-3 w-full animate-pulse rounded bg-muted" />
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

function RepositoryDashboardContent() {
  const { session } = useAuth();
  const params = useParams<{ repositoryId?: string | string[] }>();
  const repositoryId = getRepositoryIdParam(params.repositoryId);
  const [repository, setRepository] = useState<RegisteredRepository | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryAttempt, setRetryAttempt] = useState(0);

  useEffect(() => {
    if (!session || !repositoryId) {
      return;
    }

    let isMounted = true;
    async function loadRepository() {
      setLoading(true);
      setError(null);
      try {
        const result = await getRegisteredRepository(
          { getSession: async () => session },
          repositoryId,
        );
        if (isMounted) {
          setRepository(result);
        }
      } catch {
        if (isMounted) {
          setRepository(null);
          setError("Repository dashboard could not be loaded. It may not exist or you may not have access.");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    void loadRepository();

    return () => {
      isMounted = false;
    };
  }, [repositoryId, retryAttempt, session]);

  const visibility = repository?.visibility ?? "private";
  const isPrivate = visibility === "private";
  const statusCards = useMemo(
    () => [
      {
        title: "Repository Registered",
        value: repository ? "Active" : "Unknown",
        description: repository
          ? `Registered ${formatDate(repository.registered_at)}`
          : "Registration date unavailable.",
      },
      {
        title: "Sync Status",
        value: repository?.sync_status ?? "Unknown",
        description: "Initial managed-resource state. Indexing has not started.",
      },
      {
        title: "Default Branch",
        value: repository?.default_branch ?? "Unknown",
        description: "Branch recorded when the repository was registered.",
      },
      {
        title: "Last Updated",
        value: repository ? formatDate(repository.updated_at) : "Unknown",
        description: "Last local metadata update in RepoMind AI.",
      },
      {
        title: "Future Index Status",
        value: "Available in v0.3",
        description: "Repository indexing will appear here after the indexing sprint.",
        disabled: true,
      },
      {
        title: "Future Embedding Status",
        value: "Available in v0.3",
        description: "Embedding generation will appear here after the AI pipeline sprint.",
        disabled: true,
      },
    ],
    [repository],
  );

  if (loading) {
    return <RepositoryDashboardSkeleton />;
  }

  if (error || !repository) {
    return (
      <main className="min-h-[calc(100vh-4rem)] bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
        <section className="mx-auto max-w-4xl">
          <Link href="/repositories" className="text-sm font-medium text-primary hover:underline">
            Back to Repository List
          </Link>
          <div
            role="alert"
            className="mt-6 rounded-lg border border-destructive/40 bg-destructive/10 p-5 text-sm text-destructive"
          >
            <p className="inline-flex items-center gap-2">
              <CircleAlert aria-hidden="true" className="h-4 w-4" />
              {error ?? "Repository was not found."}
            </p>
            <button
              type="button"
              onClick={() => setRetryAttempt((currentAttempt) => currentAttempt + 1)}
              className="mt-4 inline-flex h-9 items-center justify-center gap-2 rounded-md border border-destructive/40 bg-background px-3 text-sm font-medium text-foreground outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-destructive/30"
            >
              <RefreshCw aria-hidden="true" className="h-4 w-4" />
              Retry
            </button>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <section className="mx-auto max-w-5xl">
        <Link href="/repositories" className="text-sm font-medium text-primary hover:underline">
          Back to Repository List
        </Link>

        <header className="mt-5 rounded-lg border border-border bg-card p-5 shadow-sm sm:p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="min-w-0">
              <p className="text-sm font-medium uppercase text-muted-foreground">Repository Dashboard</p>
              <h1 className="mt-3 break-words text-3xl font-semibold text-card-foreground">
                {repository.name}
              </h1>
              <p className="mt-2 break-all text-sm text-muted-foreground">{repository.full_name}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <span className="inline-flex items-center gap-1 rounded-full border border-border bg-secondary px-2 py-1 text-xs font-medium capitalize text-secondary-foreground">
                {isPrivate ? (
                  <Lock aria-hidden="true" className="h-3 w-3" />
                ) : (
                  <Globe2 aria-hidden="true" className="h-3 w-3" />
                )}
                {visibility}
              </span>
              <span className="inline-flex items-center gap-1 rounded-full border border-primary/30 bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
                <BadgeCheck aria-hidden="true" className="h-3.5 w-3.5" />
                Registered
              </span>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
            <span className="rounded-md border border-border bg-background px-2 py-1 font-medium text-foreground">
              {repository.owner_login}
            </span>
            <span className="rounded-md border border-border bg-background px-2 py-1">
              {repository.language ?? "Unknown language"}
            </span>
            {repository.html_url ? (
              <a
                href={repository.html_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 rounded-md border border-border bg-background px-2 py-1 font-medium text-foreground transition-colors hover:bg-secondary"
              >
                GitHub
                <ExternalLink aria-hidden="true" className="h-3.5 w-3.5" />
              </a>
            ) : null}
          </div>
        </header>

        <section className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3" aria-label="Repository status">
          {statusCards.map((card) => (
            <StatusCard key={card.title} {...card} />
          ))}
        </section>

        <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(280px,0.8fr)]">
          <section className="rounded-lg border border-border bg-card p-5 shadow-sm" aria-labelledby="overview-heading">
            <h2 id="overview-heading" className="text-lg font-semibold text-card-foreground">
              Repository Overview
            </h2>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">
              {repository.description || "No description provided for this repository."}
            </p>
          </section>

          <section className="rounded-lg border border-border bg-card p-5 shadow-sm" aria-labelledby="metadata-heading">
            <h2 id="metadata-heading" className="text-lg font-semibold text-card-foreground">
              Repository Metadata
            </h2>
            <dl className="mt-3">
              <MetadataRow label="Owner" value={repository.owner_login} />
              <MetadataRow label="Visibility" value={repository.visibility} />
              <MetadataRow label="Language" value={repository.language ?? "Unknown"} />
              <MetadataRow label="Default branch" value={repository.default_branch} />
              <MetadataRow label="GitHub id" value={repository.github_repository_id} />
            </dl>
          </section>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <section className="rounded-lg border border-border bg-card p-5 shadow-sm" aria-labelledby="registration-heading">
            <h2 id="registration-heading" className="text-lg font-semibold text-card-foreground">
              Registration Information
            </h2>
            <dl className="mt-3">
              <MetadataRow label="Local repository id" value={repository.id} />
              <MetadataRow label="Registered" value={formatDate(repository.registered_at)} />
              <MetadataRow label="Updated" value={formatDate(repository.updated_at)} />
            </dl>
          </section>

          <section className="rounded-lg border border-border bg-card p-5 shadow-sm" aria-labelledby="sync-heading">
            <h2 id="sync-heading" className="text-lg font-semibold text-card-foreground">
              Synchronization Status
            </h2>
            <div className="mt-4 rounded-md border border-border bg-background p-4">
              <p className="inline-flex items-center gap-2 text-sm font-medium text-foreground">
                <GitBranch aria-hidden="true" className="h-4 w-4" />
                {repository.sync_status}
              </p>
              <p className="mt-2 text-sm text-muted-foreground">
                Repository registration is complete. Cloning, indexing, and embeddings are not enabled in this sprint.
              </p>
            </div>
          </section>
        </div>

        <section className="mt-6 rounded-lg border border-border bg-card p-5 shadow-sm" aria-labelledby="future-ai-heading">
          <h2 id="future-ai-heading" className="text-lg font-semibold text-card-foreground">
            Future AI Features
          </h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border border-dashed border-border bg-secondary/50 p-4 opacity-75">
              <p className="inline-flex items-center gap-2 text-sm font-medium text-foreground">
                <Code2 aria-hidden="true" className="h-4 w-4" />
                Code Understanding
              </p>
              <p className="mt-3 text-xl font-semibold text-foreground">Available in v0.3</p>
              <p className="mt-2 text-sm text-muted-foreground">
                File parsing and repository indexing will power this section later.
              </p>
            </div>
            <div className="rounded-lg border border-dashed border-border bg-secondary/50 p-4 opacity-75">
              <p className="inline-flex items-center gap-2 text-sm font-medium text-foreground">
                <Bot aria-hidden="true" className="h-4 w-4" />
                Repository Chat
              </p>
              <p className="mt-3 text-xl font-semibold text-foreground">Available in v0.3</p>
              <p className="mt-2 text-sm text-muted-foreground">
                RAG chat will activate after embeddings and citations are implemented.
              </p>
            </div>
            <div className="rounded-lg border border-dashed border-border bg-secondary/50 p-4 opacity-75 sm:col-span-2">
              <p className="inline-flex items-center gap-2 text-sm font-medium text-foreground">
                <Sparkles aria-hidden="true" className="h-4 w-4" />
                AI Engineering Insights
              </p>
              <p className="mt-3 text-xl font-semibold text-foreground">Available in v0.3</p>
              <p className="mt-2 text-sm text-muted-foreground">
                Architecture summaries, dependency insights, and code explanations remain intentionally disabled.
              </p>
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}

export default function RepositoryDashboardPage() {
  return (
    <RequireAuth>
      <RepositoryDashboardContent />
    </RequireAuth>
  );
}