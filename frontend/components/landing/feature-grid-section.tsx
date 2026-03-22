import { Route, Shield, Users, GitCompare, Database, Star } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

const features = [
  {
    icon: Route,
    title: "Context-first routing",
    description: "Every prompt is routed through the context agent, ensuring all changes are reviewed before execution.",
  },
  {
    icon: Shield,
    title: "Risk-aware plan review",
    description: "Automatic risk assessment based on historical patterns, known issues, and team-defined policies.",
  },
  {
    icon: Users,
    title: "Human-in-the-loop approvals",
    description: "Configurable approval workflows that keep humans in control of critical decisions.",
  },
  {
    icon: GitCompare,
    title: "Git diff-aware checks",
    description: "Understands code changes in context, comparing against baseline and detecting potential conflicts.",
  },
  {
    icon: Database,
    title: "Issue-only indexing memory",
    description: "Builds institutional memory from resolved issues, not noise—focused context that improves over time.",
  },
  {
    icon: Star,
    title: "Explainable trust scoring",
    description: "Transparent scoring system that shows exactly why a plan was approved, flagged, or blocked.",
  },
]

export function FeatureGridSection() {
  return (
    <section id="product" className="border-y border-border bg-muted/30 py-20 md:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground md:text-4xl">
            Built for AI-Powered Teams
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Everything you need to make AI coding safer, traceable, and aligned with your team's proven logic.
          </p>
        </div>

        <div className="mt-16 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title} className="border-border bg-card">
              <CardHeader>
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-foreground">{feature.title}</CardTitle>
                <CardDescription className="text-muted-foreground">
                  {feature.description}
                </CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
