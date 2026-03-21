import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, Play, Shield, AlertTriangle, CheckCircle2, GitBranch } from "lucide-react"

export function HeroSection() {
  return (
    <section className="relative overflow-hidden py-20 md:py-32">
      <div className="container mx-auto px-4">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          {/* Left Content */}
          <div className="flex flex-col gap-6">
            <Badge variant="secondary" className="w-fit">
              Context-first AI governance
            </Badge>
            <h1 className="text-pretty text-4xl font-bold tracking-tight text-foreground md:text-5xl lg:text-6xl">
              Stop AI Coding Regressions Before They Ship
            </h1>
            <p className="max-w-xl text-lg leading-relaxed text-muted-foreground">
              ContextSuite reviews every plan against historical issue memory, approved constraints, and risk policies.
            </p>
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <Button size="lg" asChild>
                <Link href="/signup">
                  Get Started
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link href="#demo">
                  <Play className="mr-2 h-4 w-4" />
                  See Demo
                </Link>
              </Button>
            </div>
          </div>

          {/* Right Content - Dashboard Mockup */}
          <div className="relative">
            <div className="rounded-xl border border-border bg-card p-4 shadow-2xl">
              <div className="mb-4 flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-red-400" />
                <div className="h-3 w-3 rounded-full bg-yellow-400" />
                <div className="h-3 w-3 rounded-full bg-green-400" />
                <span className="ml-4 text-xs text-muted-foreground">ContextSuite Dashboard</span>
              </div>
              <div className="space-y-3">
                {/* Risk Flags Card */}
                <div className="rounded-lg border border-border bg-background p-3">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-medium text-foreground">Risk Assessment</span>
                    <Badge variant="outline" className="border-amber-500 text-amber-600">
                      <AlertTriangle className="mr-1 h-3 w-3" />
                      2 Flags
                    </Badge>
                  </div>
                  <div className="space-y-2 text-xs text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-3 w-3 text-amber-500" />
                      <span>Similar change caused issue #234 on 2024-01-15</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Shield className="h-3 w-3 text-primary" />
                      <span>Constraint: No direct DB writes in auth module</span>
                    </div>
                  </div>
                </div>

                {/* Approval State Card */}
                <div className="rounded-lg border border-border bg-background p-3">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-medium text-foreground">Approval State</span>
                    <Badge className="bg-accent text-accent-foreground">
                      <CheckCircle2 className="mr-1 h-3 w-3" />
                      Approved
                    </Badge>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    <p>Approved by: Sarah Chen (Tech Lead)</p>
                    <p>Trust Score: 92/100</p>
                  </div>
                </div>

                {/* Issue Context Card */}
                <div className="rounded-lg border border-border bg-background p-3">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-medium text-foreground">Issue Context</span>
                    <GitBranch className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="space-y-1 text-xs text-muted-foreground">
                    <p>Linked: AUTH-234, AUTH-189</p>
                    <p>Memory matches: 3 prior incidents</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
