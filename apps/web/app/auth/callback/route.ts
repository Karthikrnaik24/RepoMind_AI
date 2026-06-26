import { NextRequest, NextResponse } from "next/server";

import { createServerSupabaseClient } from "../../../lib/supabase/server";

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const redirectOrigin = requestUrl.origin;

  try {
    const supabase = createServerSupabaseClient();

    if (code) {
      const { error } = await supabase.auth.exchangeCodeForSession(code);
      if (error) {
        return NextResponse.redirect(`${redirectOrigin}/login?error=authentication_failed`);
      }
    }

    const { data } = await supabase.auth.getSession();
    if (data.session) {
      return NextResponse.redirect(`${redirectOrigin}/dashboard`);
    }
  } catch {
    return NextResponse.redirect(`${redirectOrigin}/login?error=authentication_failed`);
  }

  return NextResponse.redirect(`${redirectOrigin}/login?error=authentication_failed`);
}
