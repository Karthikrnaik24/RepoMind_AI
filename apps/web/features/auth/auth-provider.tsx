"use client";

import React from "react";
import type { ReactNode } from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { Session, SupabaseClient, User } from "@supabase/supabase-js";

import { createBrowserSupabaseClient } from "../../lib/supabase/client";

import { AuthContext } from "./auth-context";

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const supabaseRef = useRef<SupabaseClient | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const getSupabaseClient = useCallback(() => {
    if (!supabaseRef.current) {
      supabaseRef.current = createBrowserSupabaseClient();
    }

    return supabaseRef.current;
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

  const signOut = useCallback(async () => {
    try {
      const supabase = getSupabaseClient();
      await supabase.auth.signOut();
    } finally {
      setSession(null);
      setUser(null);
      setLoading(false);
    }
  }, [getSupabaseClient]);

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
    () => ({ loading, refreshSession, session, signOut, user }),
    [loading, refreshSession, session, signOut, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
