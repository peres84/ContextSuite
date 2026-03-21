import type { Metadata } from "next"
import Link from "next/link"
import { LoginForm } from "@/components/auth/login-form"

export const metadata: Metadata = {
  title: "Log In - ContextSuite",
  description: "Secure sign-in for ContextSuite workspaces",
}

export default function LoginPage() {
  return (
    <div className="flex min-h-screen">
      {/* Left Panel - Brand */}
      <div className="hidden flex-1 flex-col justify-between bg-primary p-12 lg:flex">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-foreground">
            <span className="text-lg font-bold text-primary">CS</span>
          </div>
          <span className="text-xl font-semibold text-primary-foreground">ContextSuite</span>
        </Link>

        <div className="max-w-md">
          <h1 className="text-3xl font-bold text-primary-foreground">
            Context-first AI governance for your team
          </h1>
          <p className="mt-4 text-lg text-primary-foreground/80">
            From prompt to approved execution, ContextSuite adds memory and governance to AI coding workflows.
          </p>
        </div>

        {/* Dashboard Preview */}
        <div className="rounded-xl border border-primary-foreground/20 bg-primary-foreground/10 p-6">
          <div className="mb-4 flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-400" />
            <span className="text-sm text-primary-foreground/70">Live Dashboard Preview</span>
          </div>
          <div className="space-y-3">
            <div className="h-4 w-3/4 rounded bg-primary-foreground/20" />
            <div className="h-4 w-1/2 rounded bg-primary-foreground/20" />
            <div className="h-4 w-2/3 rounded bg-primary-foreground/20" />
          </div>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex flex-1 items-center justify-center bg-background p-8">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="mb-8 flex items-center justify-center lg:hidden">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <span className="text-lg font-bold text-primary-foreground">CS</span>
              </div>
              <span className="text-xl font-semibold text-foreground">ContextSuite</span>
            </Link>
          </div>

          <div className="mb-8 text-center lg:text-left">
            <h2 className="text-2xl font-bold text-foreground">Welcome back</h2>
            <p className="mt-2 text-muted-foreground">
              Secure sign-in for ContextSuite workspaces
            </p>
          </div>

          <LoginForm />

          <p className="mt-8 text-center text-xs text-muted-foreground">
            By continuing, you agree to our{" "}
            <Link href="#terms" className="underline hover:text-foreground">
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link href="#privacy" className="underline hover:text-foreground">
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
