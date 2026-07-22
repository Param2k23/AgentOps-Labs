import * as React from 'react'

import { cn } from '@/lib/utils'

type ButtonVariant = 'default' | 'secondary' | 'ghost' | 'outline'
type ButtonSize = 'default' | 'sm' | 'lg' | 'icon'

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
}

const variantClasses: Record<ButtonVariant, string> = {
  default:
    'bg-primary text-primary-foreground shadow hover:bg-primary/90 focus-visible:ring-2 focus-visible:ring-ring',
  secondary:
    'bg-secondary text-secondary-foreground hover:bg-secondary/80 focus-visible:ring-2 focus-visible:ring-ring',
  ghost:
    'bg-transparent text-foreground hover:bg-accent hover:text-accent-foreground',
  outline:
    'border border-border bg-background text-foreground hover:bg-accent hover:text-accent-foreground',
}

const sizeClasses: Record<ButtonSize, string> = {
  default: 'h-10 px-4 py-2',
  sm: 'h-9 rounded-md px-3',
  lg: 'h-11 rounded-md px-8',
  icon: 'h-10 w-10',
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  function Button(
    { className, variant = 'default', size = 'default', type = 'button', ...props },
    ref,
  ) {
    return (
      <button
        ref={ref}
        type={type}
        className={cn(
          'inline-flex items-center justify-center gap-2 rounded-xl text-sm font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50',
          variantClasses[variant],
          sizeClasses[size],
          className,
        )}
        {...props}
      />
    )
  },
)
