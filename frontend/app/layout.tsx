import type { Metadata } from 'next'
import { Inter } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
});

import { DashboardShell } from '@/components/dashboard-shell'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from "@/components/ui/toaster"
import './globals.css'

export const metadata: Metadata = {
  title: 'Enterprise Agent Lab',
  description: 'Enterprise AI agent execution and benchmarking platform.',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
          <DashboardShell>{children}</DashboardShell>
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  )
}
