"use client";

import React from "react";
import Link from "next/link";
import { Search } from "lucide-react";

import { useAuth } from "../features/auth/auth-hooks";

import { ThemeToggle } from "./theme-toggle";

export function SiteNav() {
  const { loading, session, signOut } = useAuth();
  const isAuthenticated = Boolean(session);

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
      <nav className="mx-auto flex min-h-16 w-full max-w-7xl flex-col gap-3 px-4 py-3 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <div className="flex items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <span className="flex h-8 w-8 items-center justify-center rounded-md border border-border bg-foreground text-xs font-bold text-background">
              RM
            </span>
            <span>RepoMind AI</span>
          </Link>
          <div className="flex items-center gap-2 lg:hidden">
            <ThemeToggle />
          </div>
        </div>

        <div className="flex flex-1 flex-col gap-3 lg:max-w-3xl lg:flex-row lg:items-center lg:justify-end">
          <label className="relative block flex-1 lg:max-w-sm">
            <span className="sr-only">Search repositories</span>
            <Search aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="search"
              placeholder="Search repositories, files, or questions"
              className="h-10 w-full rounded-md border border-border bg-secondary/55 pl-9 pr-3 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground focus:border-ring focus:bg-background focus:ring-2 focus:ring-ring/20"
            />
          </label>

          <div className="flex items-center gap-2">
            <div className="hidden lg:block">
              <ThemeToggle />
            </div>
            {!loading && isAuthenticated ? (
              <>
                <Link
                  href="/dashboard"
                  className="inline-flex h-9 items-center justify-center rounded-md border border-border bg-background px-3 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
                >
                  Dashboard
                </Link>
                <button
                  type="button"
                  onClick={() => void signOut()}
                  className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                >
                  Logout
                </button>
              </>
            ) : null}
            {!loading && !isAuthenticated ? (
              <>
                <Link
                  href="/login"
                  className="inline-flex h-9 items-center justify-center rounded-md border border-border bg-background px-3 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
                >
                  Sign in
                </Link>
                <Link
                  href="/login"
                  className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                >
                  Get started
                </Link>
              </>
            ) : null}
          </div>
        </div>
      </nav>
    </header>
  );
}


