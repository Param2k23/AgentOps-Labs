type PageShellProps = {
  title: string
  description: string
  label: string
}

export function PageShell({ title, description, label }: PageShellProps) {
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

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
          <p className="text-sm font-medium text-muted-foreground">Overview</p>
          <p className="mt-3 text-lg font-semibold text-foreground">Placeholder content</p>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            This route is intentionally empty until the next milestone adds data
            flow and backend integration.
          </p>
        </div>

        <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
          <p className="text-sm font-medium text-muted-foreground">Status</p>
          <p className="mt-3 text-lg font-semibold text-foreground">Bootstrap ready</p>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            Layout, navigation, and theme switching are configured for the app.
          </p>
        </div>

        <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
          <p className="text-sm font-medium text-muted-foreground">Next step</p>
          <p className="mt-3 text-lg font-semibold text-foreground">Task 1.4</p>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            CI/CD will be added separately without changing this frontend shell.
          </p>
        </div>
      </div>
    </section>
  )
}
