import type { Metadata } from "next";
import type { ReactNode } from "react";

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
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}

