'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Menu,
  Globe2,
  LayoutDashboard,
  PlaySquare,
  ScrollText,
  Settings2,
  Trophy,
  FileText,
} from 'lucide-react'
import { useState } from 'react'

import { ThemeToggle } from '@/components/theme-toggle'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const navigationItems = [
  { label: 'Dashboard', href: '/', icon: LayoutDashboard },
  { label: 'Worlds', href: '/worlds', icon: Globe2 },
  { label: 'Documents', href: '/documents', icon: FileText },
  { label: 'Tasks', href: '/tasks', icon: ScrollText },
  { label: 'Runs', href: '/runs', icon: PlaySquare },
  { label: 'Leaderboard', href: '/leaderboard', icon: Trophy },
  { label: 'Settings', href: '/settings', icon: Settings2 },
] as const

type DashboardShellProps = {
  children: React.ReactNode
}

export function DashboardShell({ children }: DashboardShellProps) {
  const pathname = usePathname()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto grid min-h-screen max-w-[1600px] lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside
          className={cn(
            'border-b border-border/70 bg-card/60 px-4 py-5 backdrop-blur-xl lg:min-h-screen lg:border-b-0 lg:border-r lg:px-6',
            mobileNavOpen ? 'block' : 'hidden lg:block',
          )}
        >
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">
                Enterprise Agent Lab
              </p>
              <h1 className="mt-1 text-lg font-semibold">Control Plane</h1>
            </div>
          </div>

          <nav className={cn('mt-6 space-y-1', mobileNavOpen ? 'block' : 'block')}>
            {navigationItems.map((item) => {
              const active =
                item.href === '/' ? pathname === '/' : pathname.startsWith(item.href)

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
                    active
                      ? 'bg-primary text-primary-foreground shadow-sm'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
                  )}
                  onClick={() => setMobileNavOpen(false)}
                >
                  <item.icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>

          <div className="mt-8 rounded-2xl border border-border bg-background/70 p-4">
            <p className="text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">
              Platform Status
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              Bootstrap complete. Backend and dashboard shells are ready for the
              next milestone.
            </p>
          </div>
        </aside>

        <div className="flex min-h-screen flex-col">
          <header className="sticky top-0 z-20 border-b border-border/70 bg-background/80 backdrop-blur-xl">
            <div className="flex items-center gap-3 px-4 py-4 sm:px-6 lg:px-8">
              <Button
                type="button"
                variant="outline"
                size="icon"
                className="lg:hidden"
                aria-label="Toggle navigation"
                onClick={() => setMobileNavOpen((current) => !current)}
              >
                <Menu className="h-4 w-4" />
              </Button>

              <div className="flex min-w-0 flex-1 items-center gap-3">
                <div className="hidden rounded-2xl border border-border bg-card px-4 py-2 sm:block sm:min-w-[280px]">
                  <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
                    Search
                  </p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Search worlds, tasks, and runs
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <ThemeToggle />
                <Button type="button" variant="outline" className="rounded-full">
                  Profile
                </Button>
              </div>
            </div>
          </header>

          <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
            <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">{children}</div>
          </main>
        </div>
      </div>
    </div>
  )
}
