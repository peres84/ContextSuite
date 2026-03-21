import { ArrowRight, TrendingDown, Clock, FileText } from "lucide-react"

export function ProblemOutcomeSection() {
  return (
    <section className="border-y border-border bg-muted/30 py-16">
      <div className="container mx-auto px-4">
        <div className="grid items-center gap-8 md:grid-cols-3">
          {/* Problem */}
          <div className="text-center md:text-left">
            <p className="text-lg font-medium text-muted-foreground">The Problem</p>
            <p className="mt-2 text-xl font-semibold text-foreground">
              Teams keep re-breaking old logic
            </p>
          </div>

          {/* Arrow */}
          <div className="hidden items-center justify-center md:flex">
            <ArrowRight className="h-8 w-8 text-primary" />
          </div>

          {/* Outcome */}
          <div className="text-center md:text-right">
            <p className="text-lg font-medium text-muted-foreground">The Outcome</p>
            <p className="mt-2 text-xl font-semibold text-foreground">
              ContextSuite catches risky plans before execution
            </p>
          </div>
        </div>

        {/* Metrics */}
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          <div className="flex items-center gap-4 rounded-lg border border-border bg-card p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <TrendingDown className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">73%</p>
              <p className="text-sm text-muted-foreground">Fewer repeated incidents</p>
            </div>
          </div>
          <div className="flex items-center gap-4 rounded-lg border border-border bg-card p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent/20">
              <Clock className="h-6 w-6 text-accent" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">2x</p>
              <p className="text-sm text-muted-foreground">Faster onboarding</p>
            </div>
          </div>
          <div className="flex items-center gap-4 rounded-lg border border-border bg-card p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <FileText className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">100%</p>
              <p className="text-sm text-muted-foreground">Explainable approval history</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
