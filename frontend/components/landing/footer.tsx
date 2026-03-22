import Link from "next/link"
import Image from "next/image"

const footerLinks = {
  Product: [
    { label: "Features", href: "#product" },
    { label: "How It Works", href: "#how-it-works" },
    { label: "Pricing", href: "#pricing" },
    { label: "Integrations", href: "#integrations" },
  ],
  Resources: [
    { label: "Documentation", href: "#docs" },
    { label: "API Reference", href: "#api" },
    { label: "Blog", href: "#blog" },
    { label: "Changelog", href: "#changelog" },
  ],
  Company: [
    { label: "About", href: "#about" },
    { label: "Careers", href: "#careers" },
    { label: "Contact", href: "#contact" },
    { label: "Security", href: "#security" },
  ],
  Legal: [
    { label: "Privacy Policy", href: "#privacy" },
    { label: "Terms of Service", href: "#terms" },
    { label: "Cookie Policy", href: "#cookies" },
  ],
}

export function Footer() {
  return (
    <footer className="border-t border-border bg-card py-12 md:py-16">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-5">
          {/* Brand */}
          <div className="lg:col-span-1">
            <Link href="/" className="flex items-center">
              <Image
                src="/images/logotype.png"
                alt="ContextSuite"
                width={160}
                height={40}
                className="h-8 w-auto"
              />
            </Link>
            <p className="mt-4 text-sm text-muted-foreground">
              Context-first AI governance for development teams.
            </p>
          </div>

          {/* Links */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h3 className="font-semibold text-foreground">{category}</h3>
              <ul className="mt-4 space-y-3">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-border pt-8 md:flex-row">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} ContextSuite. All rights reserved.
          </p>
          <div className="flex items-center gap-6">
            <Link href="#twitter" className="text-sm text-muted-foreground hover:text-foreground">
              Twitter
            </Link>
            <Link href="#github" className="text-sm text-muted-foreground hover:text-foreground">
              GitHub
            </Link>
            <Link href="#linkedin" className="text-sm text-muted-foreground hover:text-foreground">
              LinkedIn
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
