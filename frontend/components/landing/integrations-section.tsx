const integrations = [
  { name: "GitHub", logo: "GH" },
  { name: "GitLab", logo: "GL" },
  { name: "VS Code", logo: "VS" },
  { name: "Slack", logo: "SL" },
  { name: "Telegram", logo: "TG" },
  { name: "Jira", logo: "JR" },
]

export function IntegrationsSection() {
  return (
    <section className="py-20 md:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            Works with your current dev workflow
          </h2>
          <p className="mt-2 text-muted-foreground">
            Plug into the tools your team already uses.
          </p>
        </div>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-6 md:gap-8">
          {integrations.map((integration) => (
            <div
              key={integration.name}
              className="flex h-16 w-24 items-center justify-center rounded-lg border border-border bg-card transition-all hover:border-primary/50 hover:shadow-sm"
              title={integration.name}
            >
              <span className="text-lg font-semibold text-muted-foreground transition-colors group-hover:text-primary">
                {integration.logo}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
