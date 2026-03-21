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
    <section className="py-16">
      <div className="container mx-auto px-4">
        <div className="text-center">
          <p className="text-lg text-muted-foreground">
            Works with your current dev workflow
          </p>
        </div>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-8">
          {integrations.map((integration) => (
            <div
              key={integration.name}
              className="flex h-16 w-24 items-center justify-center rounded-lg border border-border bg-card transition-colors hover:border-primary/50"
              title={integration.name}
            >
              <span className="text-lg font-semibold text-muted-foreground">
                {integration.logo}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
