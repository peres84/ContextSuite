import { User, HelpCircle, FileEdit, ClipboardCheck } from "lucide-react"

const trustCards = [
  {
    icon: User,
    title: "Who approved",
    description: "Full audit trail of every approval decision with user attribution and timestamps.",
  },
  {
    icon: HelpCircle,
    title: "Why approved",
    description: "Detailed reasoning and context for every approval, making decisions transparent.",
  },
  {
    icon: FileEdit,
    title: "What changed",
    description: "Complete diff history showing exactly what modifications were made to the codebase.",
  },
  {
    icon: ClipboardCheck,
    title: "What constraints were checked",
    description: "Record of all policies, rules, and constraints that were evaluated for each decision.",
  },
]

export function TrustSection() {
  return (
    <section id="security" className="py-20 md:py-32">
      <div className="container mx-auto px-4">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-foreground md:text-4xl">
              Every decision is traceable
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Complete transparency into your AI coding governance. Know exactly what happened, when, and why—every time.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {trustCards.map((card) => (
              <div
                key={card.title}
                className="group rounded-xl border border-border bg-card p-6 transition-colors hover:border-primary/50"
              >
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 transition-colors group-hover:bg-primary/20">
                  <card.icon className="h-5 w-5 text-primary" />
                </div>
                <h3 className="font-semibold text-foreground">{card.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{card.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
