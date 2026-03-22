import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Check } from "lucide-react"

const plans = [
  {
    name: "Individual",
    price: "$15",
    period: "/month",
    description: "Perfect for solo developers working on personal projects.",
    features: [
      "Up to 5 repos/projects",
      "Basic issue memory",
      "Email support",
      "7-day history retention",
    ],
    cta: "Start Free Setup",
    highlighted: false,
  },
  {
    name: "Starter",
    price: "$10",
    period: "/seat",
    description: "For small teams getting started with AI governance.",
    features: [
      "Unlimited repos",
      "Full issue memory",
      "Human-in-the-loop approvals",
      "30-day history retention",
      "Priority support",
    ],
    cta: "Start Free Setup",
    highlighted: true,
  },
  {
    name: "Growth",
    price: "Custom",
    period: "",
    description: "Discounted per-seat tiers for scaling teams.",
    features: [
      "Everything in Starter",
      "Volume discounts",
      "Custom integrations",
      "Unlimited history",
      "Dedicated support",
      "SLA guarantee",
    ],
    cta: "Talk to Sales",
    highlighted: false,
  },
]

const addons = [
  { name: "Slack Integration", price: "+$5/mo" },
  { name: "Telegram Integration", price: "+$5/mo" },
  { name: "Jira Plugin", price: "+$10/mo" },
]

export function PricingSection() {
  return (
    <section id="pricing" className="border-y border-border bg-muted/30 py-20 md:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground md:text-4xl">
            Simple, transparent pricing
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Start free, scale as you grow. No hidden fees.
          </p>
        </div>

        <div className="mt-16 grid gap-6 lg:grid-cols-3">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={`relative ${
                plan.highlighted
                  ? "border-primary shadow-lg"
                  : "border-border"
              }`}
            >
              {plan.highlighted && (
                <Badge className="absolute -top-3 left-1/2 -translate-x-1/2">
                  Most Popular
                </Badge>
              )}
              <CardHeader>
                <CardTitle className="text-foreground">{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-foreground">{plan.price}</span>
                  <span className="text-muted-foreground">{plan.period}</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-3 text-sm text-muted-foreground">
                      <Check className="h-4 w-4 text-accent" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter>
                <Button
                  className="w-full"
                  variant={plan.highlighted ? "default" : "outline"}
                  asChild
                >
                  <Link href="/signup">{plan.cta}</Link>
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* Add-ons */}
        <div className="mx-auto mt-12 max-w-md text-center">
          <h3 className="text-lg font-semibold text-foreground">Available Add-ons</h3>
          <div className="mt-4 flex flex-wrap justify-center gap-4">
            {addons.map((addon) => (
              <Badge key={addon.name} variant="secondary" className="text-sm">
                {addon.name} <span className="ml-1 text-muted-foreground">{addon.price}</span>
              </Badge>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
