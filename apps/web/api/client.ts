import type { Session } from "@supabase/supabase-js";

export type ApiClientOptions = {
  baseUrl?: string;
  getSession?: () => Promise<Session | null>;
  fetcher?: typeof fetch;
};

export type ApiRequestOptions = RequestInit & {
  authenticated?: boolean;
};

function getApiBaseUrl(baseUrl?: string) {
  return baseUrl ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}

export function createApiClient({ baseUrl, fetcher = fetch, getSession }: ApiClientOptions = {}) {
  const resolvedBaseUrl = getApiBaseUrl(baseUrl).replace(/\/$/, "");

  async function request(path: string, options: ApiRequestOptions = {}) {
    const { authenticated = false, headers, ...requestInit } = options;
    const requestHeaders = new Headers(headers);

    if (authenticated && getSession) {
      const session = await getSession();
      if (session?.access_token) {
        requestHeaders.set("Authorization", `Bearer ${session.access_token}`);
      }
    }

    return fetcher(`${resolvedBaseUrl}${path}`, {
      ...requestInit,
      headers: requestHeaders,
    });
  }

  return { request };
}
