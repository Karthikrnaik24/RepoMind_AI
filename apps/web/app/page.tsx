"use client";

import React from "react";
import Link from "next/link";
import { Bot, Braces, CheckCircle2, FileText, GitBranch, Github, LockKeyhole, SearchCode } from "lucide-react";

import { useAuth } from "../features/auth/auth-hooks";

const featureCards = [
  {
    icon: SearchCode,
    title: "Repository discovery",
    description: "Connect GitHub and browse repositories through clean DTOs without exposing raw provider data.",
  },
  {
    icon: GitBranch,
    title: "Managed repositories",
    description: "Register repositories as platform resources before future indexing, embeddings, and chat workflows.",
  },
  {
    icon: LockKeyhole,
    title: "Secure identity foundation",
    description: "Supabase OAuth, JWT validation, local user sync, and RBAC boundaries are built into the base.",
  },
];

const repositoryRows = [
  { name: "repomind-ai/api", language: "Python", status: "Registered" },
  { name: "repomind-ai/web", language: "TypeScript", status: "Ready" },
  { name: "repomind-ai/docs", language: "Markdown", status: "Documented" },
];

function HeroActions() {
  const { loading, session, signInWithGitHub, signInWithGoogle } = useAuth();
  const isAuthenticated = Boolean(session);

  if (loading) {
    return (
      <div className="mt-8 flex flex-col gap-3 sm:flex-row" aria-label="Loading authentication state">
        <div className="h-11 w-44 animate-pulse rounded-md bg-muted" />
        <div className="h-11 w-36 animate-pulse rounded-md bg-muted" />
      </div>
    );
  }

  if (isAuthenticated) {
    return (
      <div className="mt-8">
        <div className="flex flex-col gap-3 sm:flex-row">
          <Link
            href="/dashboard"
            className="inline-flex h-11 items-center justify-center rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground outline-none transition-colors hover:bg-primary/90 focus:ring-2 focus:ring-primary/30"
          >
            Go to Dashboard
          </Link>
          <Link
            href="/repositories"
            className="inline-flex h-11 items-center justify-center rounded-md border border-border bg-background px-5 text-sm font-medium text-foreground outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-primary/20"
          >
            Repositories
          </Link>
        </div>
        <p className="mt-4 text-sm text-muted-foreground">
          You are signed in. Continue from your dashboard or manage registered repositories.
        </p>
      </div>
    );
  }

  return (
    <div className="mt-8">
      <div className="flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          onClick={() => void signInWithGoogle()}
          className="inline-flex h-11 items-center justify-center rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground outline-none transition-colors hover:bg-primary/90 focus:ring-2 focus:ring-primary/30"
        >
          Continue with Google
        </button>
        <button
          type="button"
          onClick={() => void signInWithGitHub()}
          className="inline-flex h-11 items-center justify-center gap-2 rounded-md border border-border bg-background px-5 text-sm font-medium text-foreground outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-primary/20"
        >
          <Github aria-hidden="true" className="h-4 w-4" />
          Continue with GitHub
        </button>
      </div>
      <p className="mt-4 text-sm text-muted-foreground">
        New and existing accounts are supported. Linked providers remain attached to one user.
      </p>
    </div>
  );
}

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <section className="border-b border-border">
        <div className="mx-auto grid max-w-7xl items-center gap-10 px-4 py-16 sm:px-6 lg:min-h-[calc(100vh-4rem)] lg:grid-cols-[1.02fr_0.98fr] lg:px-8 lg:py-20">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-secondary px-3 py-1 text-sm font-medium text-muted-foreground">
              <Bot aria-hidden="true" className="h-4 w-4 text-primary" />
              AI Software Engineer for GitHub Repositories
            </div>
            <h1 className="mt-6 max-w-4xl text-5xl font-semibold leading-tight tracking-tight sm:text-6xl lg:text-7xl">
              Understand every repository before you change it.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
              RepoMind AI gives engineering teams a secure foundation for connecting GitHub,
              managing repositories, and preparing codebases for source-aware assistance.
            </p>
            <HeroActions />
          </div>

          <div className="rounded-lg border border-border bg-card shadow-sm">
            <div className="flex items-center justify-between border-b border-border px-4 py-3">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-destructive" />
                <span className="h-3 w-3 rounded-full bg-amber-500" />
                <span className="h-3 w-3 rounded-full bg-primary" />
              </div>
              <span className="text-xs font-medium text-muted-foreground">Repository preview</span>
            </div>
            <div className="space-y-4 p-5">
              <div className="rounded-md border border-border bg-secondary/55 p-4">
                <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                  <Braces aria-hidden="true" className="h-4 w-4 text-accent" />
                  repomind-ai/platform
                </div>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">
                  A managed repository card with identity, metadata, sync status, and future AI readiness.
                </p>
              </div>
              <div className="divide-y divide-border rounded-md border border-border">
                {repositoryRows.map((row) => (
                  <div key={row.name} className="grid gap-3 p-4 sm:grid-cols-[1fr_auto] sm:items-center">
                    <div>
                      <p className="text-sm font-medium text-foreground">{row.name}</p>
                      <p className="mt-1 text-xs text-muted-foreground">{row.language}</p>
                    </div>
                    <span className="inline-flex w-fit items-center gap-1 rounded-full border border-border bg-background px-2 py-1 text-xs text-muted-foreground">
                      <CheckCircle2 aria-hidden="true" className="h-3.5 w-3.5 text-primary" />
                      {row.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="mx-auto grid max-w-7xl gap-4 px-4 py-12 sm:px-6 md:grid-cols-3 lg:px-8">
        {featureCards.map((feature) => {
          const Icon = feature.icon;

          return (
            <article key={feature.title} className="rounded-lg border border-border bg-card p-5 shadow-sm">
              <Icon aria-hidden="true" className="h-5 w-5 text-primary" />
              <h2 className="mt-4 text-lg font-semibold text-card-foreground">{feature.title}</h2>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">{feature.description}</p>
            </article>
          );
        })}
      </section>

      <section id="docs" className="border-y border-border bg-secondary/35">
        <div className="mx-auto grid max-w-7xl gap-6 px-4 py-12 sm:px-6 lg:grid-cols-[0.75fr_1fr] lg:px-8">
          <div>
            <FileText aria-hidden="true" className="h-5 w-5 text-primary" />
            <h2 className="mt-4 text-2xl font-semibold tracking-tight">Built from documentation outward.</h2>
          </div>
          <p className="text-sm leading-6 text-muted-foreground">
            Product vision, architecture, database design, API contracts, security, deployment, testing,
            authentication, and GitHub integration docs stay aligned with implementation milestones.
          </p>
        </div>
      </section>

      <section id="pricing" className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
          <p className="text-sm font-medium uppercase text-muted-foreground">Pricing</p>
          <h2 className="mt-3 text-2xl font-semibold tracking-tight">Coming soon for teams and solo builders.</h2>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
            RepoMind AI is focused on a production-ready foundation first. Billing will arrive after
            repository intelligence workflows are ready for real usage.
          </p>
        </div>
      </section>
    </main>
  );
}
