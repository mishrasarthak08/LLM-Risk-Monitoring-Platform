import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "VERITAS AI — Enterprise LLM Reliability & Model Governance",
  description: "Defense-grade evaluation, observability, regression CI gating, and SR 11-7 compliance for generative AI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark bg-slate-950 text-slate-100 antialiased">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
