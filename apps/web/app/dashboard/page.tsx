"use client";

import React from "react";

import { useAuth } from "../../features/auth/auth-hooks";
import { RequireAuth } from "../../features/auth/require-auth";

function DashboardContent() {
  const { signOut, user } = useAuth();

  return (
    <main className="min-h-screen bg-background px-6 py-10 text-foreground">
      <section className="mx-auto max-w-4xl">
        <p className="text-sm font-medium uppercase tracking-wide text-muted-foreground">Dashboard</p>
        <div className="mt-4 flex flex-col gap-4 border-b border-border pb-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">RepoMind AI</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Signed in as {user?.email ?? "unknown user"}
            </p>
          </div>
          <button
            type="button"
            onClick={() => void signOut()}
            className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Log out
          </button>
        </div>
        <div className="py-8 text-sm text-muted-foreground">
          Repository features will be introduced in a future sprint.
        </div>
      </section>
    </main>
  );
}

export default function DashboardPage() {
  return (
    <RequireAuth>
      <DashboardContent />
    </RequireAuth>
  );
}
