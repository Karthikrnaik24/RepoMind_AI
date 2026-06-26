"use client";

import React from "react";
import { Suspense, useEffect, useState } from "react";
import Image from "next/image";
import { useSearchParams } from "next/navigation";
import type { Session, User } from "@supabase/supabase-js";
import { BadgeCheck, CircleAlert, Github } from "lucide-react";

import {
  getGitHubTokenDebugStatus,
  type GitHubTokenDebugStatus,
} from "../../api/github";
import { useAuth } from "../../features/auth/auth-hooks";
import { RequireAuth } from "../../features/auth/require-auth";

const githubLinkErrorMessages: Record<string, string> = {
  identity_already_linked: "This GitHub account is already linked.",
  oauth_cancelled: "GitHub linking was cancelled.",
  oauth_failed: "GitHub linking failed. Please try again.",
  provider_unavailable: "GitHub linking is unavailable right now.",
};

const isDeveloperMode = process.env.NODE_ENV !== "production";

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

type GitHubDebugCardProps = {
  error: string | null;
  loading: boolean;
  status: GitHubTokenDebugStatus | null;
};

function formatDebugValue(value: boolean | undefined) {
  if (value === undefined) {
    return "Unknown";
  }

  return value ? "Yes" : "No";
}

function GitHubDebugCard({ error, loading, status }: GitHubDebugCardProps) {
  return (
    <section className="pb-8">
      <div className="rounded-lg border border-dashed border-border bg-card p-5 shadow-sm">
        <div>
          <p className="text-xs font-medium uppercase text-muted-foreground">Developer Mode</p>
          <h2 className="mt-2 text-lg font-semibold text-card-foreground">GitHub Token Debug</h2>
        </div>

        {loading ? <p className="mt-4 text-sm text-muted-foreground">Checking GitHub token status...</p> : null}
        {error ? <p className="mt-4 text-sm text-destructive">{error}</p> : null}

        <dl className="mt-5 grid gap-3 sm:grid-cols-3">
          <div className="rounded-md border border-border bg-background p-3">
            <dt className="text-xs text-muted-foreground">GitHub Linked</dt>
            <dd className="mt-1 text-sm font-medium text-foreground">
              {formatDebugValue(status?.github_linked)}
            </dd>
          </div>
          <div className="rounded-md border border-border bg-background p-3">
            <dt className="text-xs text-muted-foreground">Token Available</dt>
            <dd className="mt-1 text-sm font-medium text-foreground">
              {formatDebugValue(status?.token_available)}
            </dd>
          </div>
          <div className="rounded-md border border-border bg-background p-3">
            <dt className="text-xs text-muted-foreground">Provider</dt>
            <dd className="mt-1 text-sm font-medium text-foreground">{status?.provider ?? "github"}</dd>
          </div>
        </dl>
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
  const [githubDebugStatus, setGitHubDebugStatus] = useState<GitHubTokenDebugStatus | null>(null);
  const [githubDebugLoading, setGitHubDebugLoading] = useState(false);
  const [githubDebugError, setGitHubDebugError] = useState<string | null>(null);

  useEffect(() => {
    void refreshSession();
  }, [refreshSession]);

  useEffect(() => {
    if (!isDeveloperMode || !session) {
      return;
    }

    let isMounted = true;
    async function loadGitHubDebugStatus(currentSession: Session) {
      setGitHubDebugLoading(true);
      setGitHubDebugError(null);
      try {
        const status = await getGitHubTokenDebugStatus({
          getSession: async () => currentSession,
        });
        if (isMounted) {
          setGitHubDebugStatus(status);
        }
      } catch {
        if (isMounted) {
          setGitHubDebugStatus(null);
          setGitHubDebugError("GitHub token debug is unavailable.");
        }
      } finally {
        if (isMounted) {
          setGitHubDebugLoading(false);
        }
      }
    }

    void loadGitHubDebugStatus(session);

    return () => {
      isMounted = false;
    };
  }, [session]);

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

        {isDeveloperMode ? (
          <GitHubDebugCard
            error={githubDebugError}
            loading={githubDebugLoading}
            status={githubDebugStatus}
          />
        ) : null}

        <div className="pb-8 text-sm text-muted-foreground">
          Repository features will be introduced in a future sprint.
        </div>
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