import { NextRequest, NextResponse } from "next/server";

import { createServerSupabaseClient } from "../../../lib/supabase/server";

function authenticationFailedRedirect(origin: string) {
  return NextResponse.redirect(`${origin}/login?error=authentication_failed`);
}

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const redirectOrigin = requestUrl.origin;

  try {
    const supabase = await createServerSupabaseClient();

    if (code) {
      const { error } = await supabase.auth.exchangeCodeForSession(code);
      if (error) {
        return authenticationFailedRedirect(redirectOrigin);
      }
    }

    const { data } = await supabase.auth.getSession();
    if (data.session) {
      return NextResponse.redirect(`${redirectOrigin}/dashboard`);
    }
  } catch {
    return authenticationFailedRedirect(redirectOrigin);
  }

  return authenticationFailedRedirect(redirectOrigin);
}
