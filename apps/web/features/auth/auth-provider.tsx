"use client";

import React from "react";
import type { ReactNode } from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { Session, SupabaseClient, User } from "@supabase/supabase-js";

import { createBrowserSupabaseClient } from "../../lib/supabase/client";

import { AuthContext } from "./auth-context";

type AuthProviderProps = {
  children: ReactNode;
};

function getOAuthRedirectUrl() {
  if (typeof window === "undefined") {
    return "/auth/callback";
  }

  return `${window.location.origin}/auth/callback`;
}

function getFriendlyAuthError(message: string | undefined) {
  if (!message) {
    return "The identity provider is unavailable. Please try again.";
  }

  const normalized = message.toLowerCase();
  if (normalized.includes("already") && normalized.includes("linked")) {
    return "This GitHub account is already linked.";
  }
  if (normalized.includes("cancel")) {
    return "GitHub linking was cancelled.";
  }

  return "GitHub linking could not be started. Please try again.";
}

export function AuthProvider({ children }: AuthProviderProps) {
  const router = useRouter();
  const supabaseRef = useRef<SupabaseClient | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState<string | null>(null);

  const getSupabaseClient = useCallback(() => {
    if (!supabaseRef.current) {
      supabaseRef.current = createBrowserSupabaseClient();
    }

    return supabaseRef.current;
  }, []);

  const clearAuthError = useCallback(() => {
    setAuthError(null);
  }, []);

  const refreshSession = useCallback(async () => {
    try {
      setLoading(true);
      const supabase = getSupabaseClient();
      const { data } = await supabase.auth.getSession();
      setSession(data.session ?? null);
      setUser(data.session?.user ?? null);
    } catch {
      setSession(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [getSupabaseClient]);

  const signInWithGoogle = useCallback(async () => {
    const supabase = getSupabaseClient();
    setAuthError(null);
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: getOAuthRedirectUrl(),
      },
    });
  }, [getSupabaseClient]);

  const linkGitHubIdentity = useCallback(async () => {
    const supabase = getSupabaseClient();
    setAuthError(null);
    const { error } = await supabase.auth.linkIdentity({
      provider: "github",
      options: {
        redirectTo: getOAuthRedirectUrl(),
      },
    });

    if (error) {
      setAuthError(getFriendlyAuthError(error.message));
    }
  }, [getSupabaseClient]);

  const signOut = useCallback(async () => {
    try {
      const supabase = getSupabaseClient();
      await supabase.auth.signOut();
    } finally {
      setSession(null);
      setUser(null);
      setAuthError(null);
      setLoading(false);
      router.replace("/");
    }
  }, [getSupabaseClient, router]);

  useEffect(() => {
    let isMounted = true;
    let unsubscribe: (() => void) | undefined;

    async function initializeSession() {
      try {
        const supabase = getSupabaseClient();
        const { data } = await supabase.auth.getSession();

        if (!isMounted) {
          return;
        }

        setSession(data.session ?? null);
        setUser(data.session?.user ?? null);

        const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
          setSession(nextSession ?? null);
          setUser(nextSession?.user ?? null);
          setLoading(false);
        });
        unsubscribe = () => listener.subscription.unsubscribe();
      } catch {
        if (isMounted) {
          setSession(null);
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    void initializeSession();

    return () => {
      isMounted = false;
      unsubscribe?.();
    };
  }, [getSupabaseClient]);

  const value = useMemo(
    () => ({
      authError,
      clearAuthError,
      linkGitHubIdentity,
      loading,
      refreshSession,
      session,
      signInWithGoogle,
      signOut,
      user,
    }),
    [
      authError,
      clearAuthError,
      linkGitHubIdentity,
      loading,
      refreshSession,
      session,
      signInWithGoogle,
      signOut,
      user,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
