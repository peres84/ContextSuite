import type { Metadata } from "next"
import Link from "next/link"
import Image from "next/image"
import { SignupWizard } from "@/components/auth/signup-wizard"

export const metadata: Metadata = {
  title: "Sign Up - ContextSuite",
  description: "Create your ContextSuite workspace and start preventing AI coding regressions",
}

export default function SignupPage() {
  return (
    <div className="flex min-h-screen">
      {/* Left Panel - Brand */}
      <div className="hidden flex-1 flex-col justify-between bg-primary p-12 lg:flex">
        <Link href="/" className="flex items-center">
          <Image
            src="/images/logotype.png"
            alt="ContextSuite"
            width={200}
            height={50}
            className="h-10 w-auto brightness-0 invert"
          />
        </Link>

        <div className="max-w-md">
          <h1 className="text-3xl font-bold text-primary-foreground">
            Start preventing regressions today
          </h1>
          <p className="mt-4 text-lg text-primary-foreground/80">
            ContextSuite helps coding teams keep AI-generated changes aligned with proven logic, approvals, and historical issue context.
          </p>

          <div className="mt-8 space-y-4">
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-foreground/20">
                <span className="text-sm font-bold text-primary-foreground">1</span>
              </div>
              <span className="text-primary-foreground/80">Create your account</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-foreground/20">
                <span className="text-sm font-bold text-primary-foreground">2</span>
              </div>
              <span className="text-primary-foreground/80">Set up your workspace</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-foreground/20">
                <span className="text-sm font-bold text-primary-foreground">3</span>
              </div>
              <span className="text-primary-foreground/80">Choose your plan</span>
            </div>
          </div>
        </div>

        <div className="text-sm text-primary-foreground/60">
          Already have an account?{" "}
          <Link href="/login" className="text-primary-foreground underline">
            Log in
          </Link>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex flex-1 items-center justify-center bg-background p-8">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="mb-8 flex items-center justify-center lg:hidden">
            <Link href="/" className="flex items-center">
              <Image
                src="/images/logotype.png"
                alt="ContextSuite"
                width={180}
                height={45}
                className="h-10 w-auto"
              />
            </Link>
          </div>

          <SignupWizard />

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
