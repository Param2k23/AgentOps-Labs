'use client'

import { useEffect, useState } from 'react'
import { MoonStar, SunMedium } from 'lucide-react'
import { useTheme } from 'next-themes'

import { Button } from '@/components/ui/button'

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <Button
      type="button"
      variant="outline"
      size="icon"
      className="rounded-full"
      aria-label="Toggle dark mode"
      onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
      disabled={!mounted}
    >
      {mounted && resolvedTheme === 'dark' ? (
        <SunMedium className="h-4 w-4" />
      ) : (
        <MoonStar className="h-4 w-4" />
      )}
    </Button>
  )
}
