# ContextSuite Logo System Prompts

## Purpose
This document provides production-ready system prompts for generating a logo concept for ContextSuite using Nano Banana or Flux 2 Pro.

Use these prompts as a base. Replace placeholders if needed.

---

## Brand Brief (Reference)
- Brand name: ContextSuite
- Category: AI governance and memory layer for coding assistants
- Core traits: trustworthy, technical, modern, precise, calm confidence
- Audience: engineering teams, CTOs, platform/dev productivity leaders
- Visual direction: clean geometry, strong legibility, no mascot, no clutter
- Color direction:
  - Deep Blue: #1A4DFF
  - Mint Accent: #18C29C
  - Text Dark: #0F172A
  - Light Surface: #F8FAFC

---

## System Prompt (Universal)
You are an expert brand identity and logo design model. Generate logo concepts that are professional, scalable, and production-friendly.

Design requirements:
- Create a modern, minimal logo for the brand ContextSuite.
- The logo must communicate: context intelligence, safety, approval flow, and technical reliability.
- Prefer abstract geometric symbols or monogram-based marks (C + S forms are acceptable).
- Keep shapes clean and simple for use in app icon, navbar, docs, and social profile.
- Ensure high legibility at small sizes (16px, 24px, 32px).
- No photorealism, no 3D bevel effects, no heavy gradients, no mascot characters.
- Avoid visual clichés such as generic robot heads, chat bubbles, or brain icons.
- Produce a premium SaaS style suitable for B2B developer tooling.

Composition requirements:
- Provide one symbol + wordmark lockup and one symbol-only variant.
- Use balanced spacing and optical alignment.
- Keep stroke and shape weights consistent.

Color requirements:
- Primary output on light background using Deep Blue (#1A4DFF) and Mint (#18C29C).
- Include monochrome black and monochrome white variants.

Typography direction:
- Wordmark should feel technical and contemporary.
- Avoid playful or decorative styles.

Output requirements:
- Return logo concepts that can be translated into vector design.
- Keep details simple enough for SVG reproduction.

---

## Nano Banana Prompt Pack

### Prompt A (Primary)
Design a logo for ContextSuite, an AI governance and memory layer for coding assistants. Style: minimal B2B SaaS, geometric, technical, trustworthy. Create a clean abstract symbol suggesting context flow and guarded approval. Include symbol + wordmark and symbol-only versions. Use Deep Blue #1A4DFF with Mint #18C29C accent on light background. Ensure it looks strong at small icon sizes. No mascots, no 3D, no clutter, no generic robot imagery.

### Prompt B (Monogram)
Create a monogram logo for ContextSuite using subtle C and S letter geometry. The mark should imply review loops, stability, and smart context routing. Keep it minimal and premium. Provide one horizontal lockup with wordmark and one app-icon version. Use a mostly blue palette with minimal mint highlight. Avoid rounded childish style.

### Prompt C (Icon-first)
Generate an icon-first logo for ContextSuite focused on a simple, memorable symbol representing protected decision flow. The symbol should work as a standalone app icon and favicon. Pair with a clean wordmark. Keep geometry crisp and balanced, optimized for developer tools branding.

---

## Flux 2 Pro Prompt Pack

### Positive Prompt
Minimal, premium SaaS logo for "ContextSuite", AI governance and context memory for coding assistants, geometric abstract mark, clean vector-like shapes, high contrast, precise spacing, modern technical wordmark, symbol plus wordmark lockup, symbol-only app icon, deep blue (#1A4DFF) with mint accent (#18C29C), light background presentation, flat design, strong small-size readability, brand identity quality, professional B2B software aesthetic.

### Negative Prompt
no mascot, no cartoon, no robot face, no brain icon, no chat bubble icon, no 3d rendering, no metallic effect, no bevel, no lens flare, no noisy texture, no photorealism, no complicated details, no illegible typography, no low contrast, no handwritten style, no playful children brand style.

### Parameter Guidance (if supported)
- Aspect ratio: 1:1 for symbol exploration, 3:2 for lockup previews
- Style strength: medium
- Variation count: 4 to 8
- Quality: high
- Seed: lock once a promising direction appears

---

## Selection Checklist
Use this checklist to evaluate outputs:
- Recognizable at 24px
- Works in monochrome
- Distinct from generic AI logos
- Looks credible for engineering leaders
- Fits navbar, favicon, docs header, and pitch deck
- Easy to recreate in SVG/Figma

---

## Final Polishing Prompt
Refine the selected concept into a final brand-ready version. Keep the same core symbol geometry. Improve spacing, optical balance, and wordmark harmony. Deliver a clean lockup, icon-only variant, monochrome variants, and a light/dark background preview while preserving minimal complexity and strong legibility.
