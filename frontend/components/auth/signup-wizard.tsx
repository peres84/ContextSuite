"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Checkbox } from "@/components/ui/checkbox"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Check, ArrowRight, ArrowLeft, CheckCircle2 } from "lucide-react"

type Step = 1 | 2 | 3 | 4

const teamSizes = [
  { value: "1", label: "Just me" },
  { value: "2-5", label: "2-5 people" },
  { value: "6-20", label: "6-20 people" },
  { value: "20+", label: "20+ people" },
]

const useCases = [
  { value: "bugfix", label: "Bug Prevention" },
  { value: "governance", label: "Governance" },
  { value: "compliance", label: "Compliance" },
  { value: "onboarding", label: "Team Onboarding" },
]

const plans = [
  {
    id: "individual",
    name: "Individual",
    price: "$15",
    period: "/month",
    description: "For solo developers",
    features: ["Up to 5 repos", "Basic issue memory", "Email support"],
  },
  {
    id: "starter",
    name: "Starter",
    price: "$10",
    period: "/seat",
    description: "For small teams",
    features: ["Unlimited repos", "Full issue memory", "Human-in-the-loop approvals"],
    popular: true,
  },
  {
    id: "growth",
    name: "Growth",
    price: "Custom",
    period: "",
    description: "For scaling teams",
    features: ["Everything in Starter", "Volume discounts", "Dedicated support"],
  },
]

const addons = [
  { id: "slack", name: "Slack Integration", price: "+$5/mo" },
  { id: "telegram", name: "Telegram Integration", price: "+$5/mo" },
  { id: "jira", name: "Jira Plugin", price: "+$10/mo" },
]

export function SignupWizard() {
  const [step, setStep] = useState<Step>(1)
  
  // Step 1: Account
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  
  // Step 2: Workspace
  const [workspaceName, setWorkspaceName] = useState("")
  const [teamSize, setTeamSize] = useState("")
  const [useCase, setUseCase] = useState("")
  
  // Step 3: Plan
  const [selectedPlan, setSelectedPlan] = useState("starter")
  const [selectedAddons, setSelectedAddons] = useState<string[]>([])

  const handleAddonToggle = (addonId: string) => {
    setSelectedAddons((prev) =>
      prev.includes(addonId)
        ? prev.filter((id) => id !== addonId)
        : [...prev, addonId]
    )
  }

  const nextStep = () => {
    if (step < 4) setStep((step + 1) as Step)
  }

  const prevStep = () => {
    if (step > 1) setStep((step - 1) as Step)
  }

  // Step 1: Account Creation
  if (step === 1) {
    return (
      <div>
        <div className="mb-6">
          <div className="mb-2 flex items-center gap-2">
            <Badge variant="secondary">Step 1 of 3</Badge>
          </div>
          <h2 className="text-2xl font-bold text-foreground">Create your account</h2>
          <p className="mt-1 text-muted-foreground">Enter your details to get started</p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            nextStep()
          }}
          className="space-y-4"
        >
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="name">Full Name</FieldLabel>
              <Input
                id="name"
                type="text"
                placeholder="Jane Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </Field>

            <Field>
              <FieldLabel htmlFor="signup-email">Work Email</FieldLabel>
              <Input
                id="signup-email"
                type="email"
                placeholder="jane@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </Field>

            <Field>
              <FieldLabel htmlFor="signup-password">Password</FieldLabel>
              <Input
                id="signup-password"
                type="password"
                placeholder="Create a strong password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </Field>

            <Field>
              <FieldLabel htmlFor="confirm-password">Confirm Password</FieldLabel>
              <Input
                id="confirm-password"
                type="password"
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </Field>
          </FieldGroup>

          <Button type="submit" className="w-full" size="lg">
            Continue
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>

          <p className="text-center text-sm text-muted-foreground lg:hidden">
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-primary hover:underline">
              Log in
            </Link>
          </p>
        </form>
      </div>
    )
  }

  // Step 2: Workspace Setup
  if (step === 2) {
    return (
      <div>
        <div className="mb-6">
          <div className="mb-2 flex items-center gap-2">
            <Badge variant="secondary">Step 2 of 3</Badge>
          </div>
          <h2 className="text-2xl font-bold text-foreground">Set up your workspace</h2>
          <p className="mt-1 text-muted-foreground">Tell us about your team</p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            nextStep()
          }}
          className="space-y-6"
        >
          <Field>
            <FieldLabel htmlFor="workspace-name">Workspace Name</FieldLabel>
            <Input
              id="workspace-name"
              type="text"
              placeholder="Acme Inc."
              value={workspaceName}
              onChange={(e) => setWorkspaceName(e.target.value)}
              required
            />
          </Field>

          <Field>
            <FieldLabel>Team Size</FieldLabel>
            <RadioGroup value={teamSize} onValueChange={setTeamSize} className="mt-2 grid grid-cols-2 gap-3">
              {teamSizes.map((size) => (
                <label
                  key={size.value}
                  className={`flex cursor-pointer items-center justify-center rounded-lg border p-3 text-sm transition-colors ${
                    teamSize === size.value
                      ? "border-primary bg-primary/5 text-foreground"
                      : "border-border text-muted-foreground hover:border-primary/50"
                  }`}
                >
                  <RadioGroupItem value={size.value} className="sr-only" />
                  {size.label}
                </label>
              ))}
            </RadioGroup>
          </Field>

          <Field>
            <FieldLabel>Primary Use Case</FieldLabel>
            <RadioGroup value={useCase} onValueChange={setUseCase} className="mt-2 grid grid-cols-2 gap-3">
              {useCases.map((uc) => (
                <label
                  key={uc.value}
                  className={`flex cursor-pointer items-center justify-center rounded-lg border p-3 text-sm transition-colors ${
                    useCase === uc.value
                      ? "border-primary bg-primary/5 text-foreground"
                      : "border-border text-muted-foreground hover:border-primary/50"
                  }`}
                >
                  <RadioGroupItem value={uc.value} className="sr-only" />
                  {uc.label}
                </label>
              ))}
            </RadioGroup>
          </Field>

          <div className="flex gap-3">
            <Button type="button" variant="outline" onClick={prevStep} className="flex-1">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
            <Button type="submit" className="flex-1">
              Continue
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </form>
      </div>
    )
  }

  // Step 3: Plan Selection
  if (step === 3) {
    return (
      <div>
        <div className="mb-6">
          <div className="mb-2 flex items-center gap-2">
            <Badge variant="secondary">Step 3 of 3</Badge>
          </div>
          <h2 className="text-2xl font-bold text-foreground">Choose your plan</h2>
          <p className="mt-1 text-muted-foreground">Select a plan that fits your needs</p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            nextStep()
          }}
          className="space-y-6"
        >
          <RadioGroup value={selectedPlan} onValueChange={setSelectedPlan} className="space-y-3">
            {plans.map((plan) => (
              <label
                key={plan.id}
                className={`relative flex cursor-pointer flex-col rounded-lg border p-4 transition-colors ${
                  selectedPlan === plan.id
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50"
                }`}
              >
                <RadioGroupItem value={plan.id} className="sr-only" />
                {plan.popular && (
                  <Badge className="absolute -top-2 right-4">Popular</Badge>
                )}
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-foreground">{plan.name}</span>
                  <span className="text-lg font-bold text-foreground">
                    {plan.price}
                    <span className="text-sm font-normal text-muted-foreground">{plan.period}</span>
                  </span>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">{plan.description}</p>
                <ul className="mt-3 flex flex-wrap gap-2">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Check className="h-3 w-3 text-accent" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </label>
            ))}
          </RadioGroup>

          <div>
            <p className="mb-3 text-sm font-medium text-foreground">Optional Add-ons</p>
            <div className="space-y-2">
              {addons.map((addon) => (
                <label
                  key={addon.id}
                  className={`flex cursor-pointer items-center justify-between rounded-lg border p-3 transition-colors ${
                    selectedAddons.includes(addon.id)
                      ? "border-primary bg-primary/5"
                      : "border-border hover:border-primary/50"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Checkbox
                      checked={selectedAddons.includes(addon.id)}
                      onCheckedChange={() => handleAddonToggle(addon.id)}
                    />
                    <span className="text-sm text-foreground">{addon.name}</span>
                  </div>
                  <span className="text-sm text-muted-foreground">{addon.price}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <Button type="button" variant="outline" onClick={prevStep} className="flex-1">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
            <Button type="submit" className="flex-1">
              Create Workspace
            </Button>
          </div>
        </form>
      </div>
    )
  }

  // Step 4: Success
  return (
    <div className="text-center">
      <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-accent/20">
        <CheckCircle2 className="h-8 w-8 text-accent" />
      </div>
      <h2 className="text-2xl font-bold text-foreground">Workspace created!</h2>
      <p className="mt-2 text-muted-foreground">
        Your workspace &ldquo;{workspaceName || "My Workspace"}&rdquo; is ready to go.
      </p>

      <Card className="mt-8 text-left">
        <CardHeader>
          <CardTitle className="text-base">Connection Endpoint</CardTitle>
          <CardDescription>Use this to connect your development environment</CardDescription>
        </CardHeader>
        <CardContent>
          <code className="block rounded-lg bg-muted p-3 text-sm text-muted-foreground">
            https://api.contextsuite.io/v1/{workspaceName?.toLowerCase().replace(/\s+/g, "-") || "workspace"}
          </code>
        </CardContent>
      </Card>

      <Button className="mt-8 w-full" size="lg" asChild>
        <Link href="#dashboard">
          Go to Dashboard
          <ArrowRight className="ml-2 h-4 w-4" />
        </Link>
      </Button>
    </div>
  )
}
