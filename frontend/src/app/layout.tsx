import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Remote Hiring Radar",
  description: "Fresh remote AI, data, agent, and vision jobs worth reviewing today.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
