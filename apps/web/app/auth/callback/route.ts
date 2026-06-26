import { NextRequest, NextResponse } from "next/server";

import { createServerSupabaseClient } from "../../../lib/supabase/server";

const githubLinkErrorMap: Record<string, string> = {
  access_denied: "oauth_cancelled",
  identity_already_exists: "identity_already_linked",
  identity_already_linked: "identity_already_linked",
  provider_disabled: "provider_unavailable",
  server_error: "oauth_failed",
};

function authenticationFailedRedirect(origin: string) {
  return NextResponse.redirect(`${origin}/login?error=authentication_failed`);
}

function dashboardGitHubErrorRedirect(origin: string, errorCode: string | null) {
  const safeCode = errorCode ? githubLinkErrorMap[errorCode] ?? "oauth_failed" : "oauth_failed";
  return NextResponse.redirect(`${origin}/dashboard?github_link_error=${safeCode}`);
}

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const oauthError = requestUrl.searchParams.get("error");
  const oauthErrorCode = requestUrl.searchParams.get("error_code") ?? oauthError;
  const redirectOrigin = requestUrl.origin;

  try {
    const supabase = await createServerSupabaseClient();

    if (code) {
      const { error } = await supabase.auth.exchangeCodeForSession(code);
      if (error) {
        const { data } = await supabase.auth.getSession();
        if (data.session) {
          return dashboardGitHubErrorRedirect(redirectOrigin, error.code ?? oauthErrorCode);
        }
        return authenticationFailedRedirect(redirectOrigin);
      }
    }

    const { data } = await supabase.auth.getSession();
    if (data.session) {
      if (oauthError) {
        return dashboardGitHubErrorRedirect(redirectOrigin, oauthErrorCode);
      }
      return NextResponse.redirect(`${redirectOrigin}/dashboard`);
    }
  } catch {
    return authenticationFailedRedirect(redirectOrigin);
  }

  return authenticationFailedRedirect(redirectOrigin);
}
