import { MessageSquare, Search, CheckCircle } from "lucide-react"

const steps = [
  {
    number: "01",
    icon: MessageSquare,
    title: "Prompt goes to Context Agent first",
    description:
      "Every AI coding request is routed through the Context Agent before execution, ensuring nothing bypasses review.",
  },
  {
    number: "02",
    icon: Search,
    title: "Plan is reviewed against prior issues and constraints",
    description:
      "The system checks the proposed changes against historical issue memory, team policies, and risk constraints.",
  },
  {
    number: "03",
    icon: CheckCircle,
    title: "Approved plans execute; outcomes are indexed",
    description:
      "Safe plans proceed to execution, and all outcomes—good or bad—are indexed for future reference.",
  },
]

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-20 md:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground md:text-4xl">
            How ContextSuite Works
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            A simple three-step process that adds memory and governance to your AI coding workflows.
          </p>
        </div>

        <div className="mt-16 grid gap-8 md:grid-cols-3">
          {steps.map((step, index) => (
            <div key={step.number} className="relative">
              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div className="absolute right-0 top-12 hidden h-0.5 w-full translate-x-1/2 bg-border md:block" />
              )}

              <div className="relative flex flex-col items-center text-center">
                <div className="relative z-10 flex h-24 w-24 items-center justify-center rounded-2xl border border-border bg-card shadow-sm">
                  <step.icon className="h-10 w-10 text-primary" />
                </div>
                <span className="mt-4 text-sm font-medium text-primary">{step.number}</span>
                <h3 className="mt-2 text-xl font-semibold text-foreground">{step.title}</h3>
                <p className="mt-3 text-muted-foreground">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
