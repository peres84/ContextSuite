import { User, HelpCircle, FileEdit, ClipboardCheck, Quote, Star } from "lucide-react"
import { Badge } from "@/components/ui/badge"

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

const testimonials = [
  {
    quote: "ContextSuite caught a regression that would have cost us a full sprint to fix in production.",
    author: "Sarah Chen",
    role: "Tech Lead, FinOps Platform",
    initials: "SC",
  },
  {
    quote: "The approval trail alone justified the tool—our compliance team finally trusts our AI workflow.",
    author: "Marcus Rivera",
    role: "VP Engineering, HealthBridge",
    initials: "MR",
  },
  {
    quote: "Onboarding new devs went from weeks of tribal knowledge transfer to days with indexed issue memory.",
    author: "Priya Patel",
    role: "Engineering Manager, DataStack",
    initials: "PP",
  },
]

export function TrustSection() {
  return (
    <>
      {/* Trust & Transparency */}
      <section id="security" className="py-20 md:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          {/* Section header */}
          <div className="mx-auto max-w-2xl text-center">
            <Badge variant="secondary" className="mb-4">
              Trust &amp; Transparency
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight text-foreground md:text-4xl">
              Every decision is traceable
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Complete transparency into your AI coding governance. Know exactly what happened, when, and why—every time.
            </p>
          </div>

          {/* Trust cards grid */}
          <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {trustCards.map((card) => (
              <div
                key={card.title}
                className="group rounded-xl border border-border bg-card p-6 transition-all hover:border-primary/50 hover:shadow-md"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 transition-colors group-hover:bg-primary/20">
                  <card.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-base font-semibold text-foreground">{card.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{card.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials — standalone section */}
      <section className="border-y border-primary/10 bg-brand-soft/30 py-20 md:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <Badge className="mb-4 bg-primary/10 text-primary hover:bg-primary/20">
              Testimonials
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight text-foreground md:text-4xl">
              What teams are saying
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Teams using ContextSuite ship with confidence.
            </p>
          </div>

          <div className="mx-auto mt-16 grid max-w-5xl gap-8 md:grid-cols-3">
            {testimonials.map((testimonial) => (
              <figure
                key={testimonial.author}
                className="relative flex flex-col rounded-2xl border border-primary/15 bg-card p-8 shadow-sm transition-all hover:border-primary/40 hover:shadow-lg"
              >
                <Quote className="mb-5 h-8 w-8 text-primary/25" />
                <div className="mb-4 flex gap-0.5">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-primary text-primary" />
                  ))}
                </div>
                <blockquote className="flex-1 text-base leading-relaxed text-foreground">
                  &ldquo;{testimonial.quote}&rdquo;
                </blockquote>
                <figcaption className="mt-8 flex items-center gap-3 border-t border-primary/10 pt-5">
                  <div className="flex h-11 w-11 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">
                    {testimonial.initials}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-foreground">{testimonial.author}</p>
                    <p className="text-xs text-muted-foreground">{testimonial.role}</p>
                  </div>
                </figcaption>
              </figure>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}
