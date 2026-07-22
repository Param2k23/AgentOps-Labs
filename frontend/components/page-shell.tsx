type PageShellProps = {
  title: string
  description: string
  label: string
  children?: React.ReactNode
}

export function PageShell({ title, description, label, children }: PageShellProps) {
  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-400">
          {label}
        </p>
        <div className="space-y-2">
          <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            {title}
          </h2>
          <p className="max-w-2xl text-sm leading-7 text-muted-foreground sm:text-base">
            {description}
          </p>
        </div>
      </div>

      {children}
    </section>
  )
}
