import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight, Calendar } from "lucide-react"

export function FinalCtaSection() {
  return (
    <section className="border-y border-border bg-primary py-20 md:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-primary-foreground md:text-4xl">
            Make AI coding safer across your team
          </h2>
          <p className="mt-4 text-lg text-primary-foreground/80">
            Start with your first workspace today and prevent regressions with context-first review.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Button size="lg" variant="secondary" asChild>
              <Link href="/signup">
                Get Started
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-primary-foreground/30 bg-transparent text-primary-foreground hover:bg-primary-foreground/10 hover:text-primary-foreground"
              asChild
            >
              <Link href="#demo">
                <Calendar className="mr-2 h-4 w-4" />
                Book a Live Demo
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
