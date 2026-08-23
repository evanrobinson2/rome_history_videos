import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Gothic Invasion — Frame Review",
  description: "Review cut-paper story frames — keep, discard, or reroll",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
