import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

const faqs = [
  {
    question: "Is this another coding assistant?",
    answer:
      "No. ContextSuite isn't a coding assistant—it's a governance layer for AI coding tools. It doesn't write code; it reviews and validates AI-generated plans against your team's historical context, constraints, and policies before execution.",
  },
  {
    question: "How does approval work?",
    answer:
      "When a plan is flagged for review, designated approvers receive a notification with full context—including risk flags, related issues, and constraint violations. They can approve, reject, or request modifications. All decisions are logged with full audit trails.",
  },
  {
    question: "What gets indexed?",
    answer:
      "ContextSuite focuses on indexing resolved issues, approved changes, and their outcomes. This creates a focused knowledge base of what went wrong and what worked—not noise from every commit or comment.",
  },
  {
    question: "Can we use it for existing repos?",
    answer:
      "Absolutely. ContextSuite can be connected to existing repositories and will begin building context from day one. For maximum value, you can optionally import historical issue data to bootstrap the memory system.",
  },
]

export function FaqSection() {
  return (
    <section className="py-20 md:py-32">
      <div className="container mx-auto px-4">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground md:text-4xl">
            Frequently Asked Questions
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Everything you need to know about ContextSuite.
          </p>
        </div>

        <div className="mx-auto mt-12 max-w-3xl">
          <Accordion type="single" collapsible className="w-full">
            {faqs.map((faq, index) => (
              <AccordionItem key={index} value={`item-${index}`}>
                <AccordionTrigger className="text-left text-foreground">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </div>
    </section>
  )
}
