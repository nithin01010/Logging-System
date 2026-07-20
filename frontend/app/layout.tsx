import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Observability Platform",
  description: "Distributed logging and tracing aggregator",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-slate-950 text-slate-100 flex min-h-screen`}>
        <Navbar />
        <main className="flex-1 p-8 overflow-y-auto">{children}</main>
      </body>
    </html>
  );
}
