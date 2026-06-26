import type { Metadata } from "next";
import type { ReactNode } from "react";

import { SiteNav } from "../components/site-nav";
import { ThemeProvider } from "../components/theme-provider";
import { AuthProvider } from "../features/auth/auth-provider";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "RepoMind AI",
  description: "Repository intelligence for engineering teams.",
};

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <AuthProvider>
            <SiteNav />
            {children}
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
