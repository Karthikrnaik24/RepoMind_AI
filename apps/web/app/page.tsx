import Link from "next/link";
import { Bot, Braces, GitBranch, LockKeyhole, SearchCode } from "lucide-react";

const featureCards = [
  {
    icon: SearchCode,
    title: "Ask across a codebase",
    description: "Find context, related files, and implementation paths without losing the thread.",
  },
  {
    icon: GitBranch,
    title: "Understand structure",
    description: "Map branches, files, chunks, dependencies, and citations into one navigable model.",
  },
  {
    icon: LockKeyhole,
    title: "Built for teams",
    description: "Clean boundaries, audit-ready architecture, and secure identity foundations from day one.",
  },
];

const repositoryRows = [
  { name: "api/indexing-pipeline", language: "Python", status: "Ready for Sprint 4" },
  { name: "web/auth-experience", language: "TypeScript", status: "Google OAuth enabled" },
  { name: "docs/architecture", language: "Markdown", status: "Production blueprint" },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <section className="border-b border-border">
        <div className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-7xl items-center gap-10 px-4 py-16 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:py-20">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-secondary px-3 py-1 text-sm font-medium text-muted-foreground">
              <Bot aria-hidden="true" className="h-4 w-4 text-primary" />
              AI Software Engineer for GitHub Repositories
            </div>
            <h1 className="mt-6 max-w-4xl text-5xl font-semibold leading-tight sm:text-6xl lg:text-7xl">
              RepoMind AI helps engineering teams understand code faster.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
              Connect repositories, index source context, and ask precise questions with citations when repository features arrive in upcoming sprints.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link
                href="/login"
                className="inline-flex h-11 items-center justify-center rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
              >
                Get started
              </Link>
              <Link
                href="/dashboard"
                className="inline-flex h-11 items-center justify-center rounded-md border border-border bg-background px-5 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
              >
                View dashboard
              </Link>
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card shadow-sm">
            <div className="flex items-center gap-2 border-b border-border px-4 py-3">
              <span className="h-3 w-3 rounded-full bg-destructive" />
              <span className="h-3 w-3 rounded-full bg-amber-500" />
              <span className="h-3 w-3 rounded-full bg-primary" />
              <span className="ml-3 text-sm text-muted-foreground">repomind-ai/workspace</span>
            </div>
            <div className="space-y-4 p-5">
              <div className="rounded-md border border-border bg-secondary/55 p-4">
                <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                  <Braces aria-hidden="true" className="h-4 w-4 text-accent" />
                  Repository intelligence preview
                </div>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">
                  Index commits, files, chunks, dependencies, and citations into a source-aware assistant designed for production teams.
                </p>
              </div>
              <div className="divide-y divide-border rounded-md border border-border">
                {repositoryRows.map((row) => (
                  <div key={row.name} className="grid gap-2 p-4 sm:grid-cols-[1fr_auto] sm:items-center">
                    <div>
                      <p className="text-sm font-medium text-foreground">{row.name}</p>
                      <p className="mt-1 text-xs text-muted-foreground">{row.language}</p>
                    </div>
                    <span className="rounded-full border border-border bg-background px-2 py-1 text-xs text-muted-foreground">
                      {row.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-4 px-4 py-12 sm:px-6 md:grid-cols-3 lg:px-8">
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
    </main>
  );
}
