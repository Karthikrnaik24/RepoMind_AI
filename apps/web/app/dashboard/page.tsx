"use client";

import React from "react";
import { Suspense, useEffect } from "react";
import Image from "next/image";
import { useSearchParams } from "next/navigation";
import { BadgeCheck, CircleAlert, Github } from "lucide-react";
import type { User } from "@supabase/supabase-js";

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

function DashboardContent() {
  const { authError, linkGitHubIdentity, refreshSession, signOut, user } = useAuth();
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
