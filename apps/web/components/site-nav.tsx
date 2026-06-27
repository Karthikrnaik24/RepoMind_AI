"use client";

import React from "react";
import Link from "next/link";
import { Search } from "lucide-react";

import { useAuth } from "../features/auth/auth-hooks";

import { ThemeToggle } from "./theme-toggle";

const navLinks = [
  { href: "/#features", label: "Features" },
  { href: "/#docs", label: "Docs" },
];

export function SiteNav() {
  const { loading, session, signOut } = useAuth();
  const isAuthenticated = Boolean(session);

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
      <nav className="mx-auto flex min-h-16 w-full max-w-7xl flex-col gap-3 px-4 py-3 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-5">
            <Link aria-label="RepoMind AI" href={isAuthenticated ? "/dashboard" : "/"} className="flex items-center gap-2 text-sm font-semibold text-foreground">
              <span className="flex h-8 w-8 items-center justify-center rounded-md border border-border bg-foreground text-xs font-bold text-background">
                RM
              </span>
              <span>RepoMind AI</span>
            </Link>
            <div className="hidden items-center gap-1 md:flex">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="rounded-md px-2.5 py-2 text-sm font-medium text-muted-foreground outline-none transition-colors hover:text-foreground focus:ring-2 focus:ring-primary/20"
                >
                  {link.label}
                </Link>
              ))}
              <Link
                href="/#pricing"
                className="rounded-md px-2.5 py-2 text-sm font-medium text-muted-foreground outline-none transition-colors hover:text-foreground focus:ring-2 focus:ring-primary/20"
              >
                Pricing <span className="text-xs text-muted-foreground">Soon</span>
              </Link>
            </div>
          </div>
          <div className="flex items-center gap-2 lg:hidden">
            <ThemeToggle />
          </div>
        </div>

        <div className="flex flex-1 flex-col gap-3 lg:max-w-3xl lg:flex-row lg:items-center lg:justify-end">
          <label className="relative block flex-1 lg:max-w-sm">
            <span className="sr-only">Search repositories</span>
            <Search
              aria-hidden="true"
              className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
            />
            <input
              type="search"
              placeholder="Search repositories, files, or questions"
              className="h-10 w-full rounded-md border border-border bg-secondary/55 pl-9 pr-3 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground focus:border-ring focus:bg-background focus:ring-2 focus:ring-ring/20"
            />
          </label>

          <div className="flex flex-wrap items-center gap-2">
            <div className="hidden lg:block">
              <ThemeToggle />
            </div>
            {!loading && isAuthenticated ? (
              <>
                <Link
                  href="/repositories"
                  className="inline-flex h-9 items-center justify-center rounded-md border border-border bg-background px-3 text-sm font-medium text-foreground outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-primary/20"
                >
                  Repositories
                </Link>
                <Link
                  href="/dashboard"
                  className="inline-flex h-9 items-center justify-center rounded-md border border-border bg-background px-3 text-sm font-medium text-foreground outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-primary/20"
                >
                  Dashboard
                </Link>
                <button
                  type="button"
                  onClick={() => void signOut()}
                  className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground outline-none transition-colors hover:bg-primary/90 focus:ring-2 focus:ring-primary/30"
                >
                  Logout
                </button>
              </>
            ) : null}
            {!loading && !isAuthenticated ? (
              <>
                <Link
                  href="/login"
                  className="inline-flex h-9 items-center justify-center rounded-md border border-border bg-background px-3 text-sm font-medium text-foreground outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-primary/20"
                >
                  Sign In
                </Link>
                <Link
                  href="/login"
                  className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground outline-none transition-colors hover:bg-primary/90 focus:ring-2 focus:ring-primary/30"
                >
                  Sign Up
                </Link>
              </>
            ) : null}
          </div>
        </div>
      </nav>
    </header>
  );
}


