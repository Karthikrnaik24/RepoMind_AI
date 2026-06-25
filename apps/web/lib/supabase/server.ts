import { createClient } from "@supabase/supabase-js";

function getSupabasePublicConfig() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!supabaseUrl || !supabaseAnonKey) {
    throw new Error("Supabase public environment variables are not configured.");
  }

  return { supabaseUrl, supabaseAnonKey };
}

export function createServerSupabaseClient() {
  const { supabaseUrl, supabaseAnonKey } = getSupabasePublicConfig();

  return createClient(supabaseUrl, supabaseAnonKey);
}
