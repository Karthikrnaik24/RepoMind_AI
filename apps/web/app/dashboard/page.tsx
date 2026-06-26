"use client";

import React from "react";
import Image from "next/image";

import { useAuth } from "../../features/auth/auth-hooks";
import { RequireAuth } from "../../features/auth/require-auth";

function getDisplayName(user: ReturnType<typeof useAuth>["user"]) {
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

function getAvatarUrl(user: ReturnType<typeof useAuth>["user"]) {
  const avatarUrl = user?.user_metadata?.avatar_url;

  return typeof avatarUrl === "string" && avatarUrl ? avatarUrl : null;
}

function getProvider(user: ReturnType<typeof useAuth>["user"]) {
  const provider = user?.app_metadata?.provider;

  return typeof provider === "string" && provider ? provider : "supabase";
}

function DashboardContent() {
  const { signOut, user } = useAuth();
  const avatarUrl = getAvatarUrl(user);
  const displayName = getDisplayName(user);
  const provider = getProvider(user);

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
              <p className="mt-1 text-xs uppercase text-muted-foreground">Provider: {provider}</p>
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
