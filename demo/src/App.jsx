const metrics = [
  { label: "Teams onboarded", value: "24" },
  { label: "Weekly reviews", value: "138" },
  { label: "Green-safe releases", value: "99.2%" },
];

const features = [
  {
    kicker: "Review memory",
    tag: "Pinned rule",
    title: "Constraint-aware review",
    copy: "Every launch checklist, brand rule, and approval note stays close to the work.",
  },
  {
    kicker: "Operator flow",
    tag: "Low noise",
    title: "Calm operator workflow",
    copy: "One page for approvals, one tone of voice, and one obvious primary action.",
  },
  {
    kicker: "Design system",
    tag: "Reusable",
    title: "Reusable design memory",
    copy: "Patterns that worked before become guidance for the next team and the next release.",
  },
];

const testimonials = [
  {
    quote: "Our brand reviews went from chaotic to calm overnight. The green-first approach keeps every team aligned.",
    name: "Maria Chen",
    role: "Head of Brand, Luma Labs",
    initials: "MC",
  },
  {
    quote: "We stopped arguing about button colors and started shipping. One palette, one signal, zero confusion.",
    name: "James Okoro",
    role: "Design Lead, Fern Studio",
    initials: "JO",
  },
  {
    quote: "The constraint-aware reviews caught brand violations we'd been missing for months. Genuinely game-changing.",
    name: "Priya Desai",
    role: "VP Engineering, GreenStack",
    initials: "PD",
  },
];

const highlights = [
  { title: "Primary stays green", copy: "Hero accents, buttons, badges, and emphasis all share one approved signal." },
  { title: "Red stays cautionary", copy: "Alerts and destructive states keep their own visual meaning instead of becoming the default CTA color." },
  { title: "Reviewers stay oriented", copy: "The interface reads as supportive and trustworthy from the first interaction to the final approval." },
];

export default function App() {
  return (
    <div className="page-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">
            GS
          </div>
          <div>
            <p className="eyebrow">Green Guard Studio</p>
            <p className="brand-summary">Brand-safe launch reviews for teams that need one clear primary signal.</p>
          </div>
        </div>
        <nav className="top-links" aria-label="Section links">
          <a className="ghost-link" href="#features">
            Features
          </a>
          <a className="ghost-link" href="#testimonials">
            Testimonials
          </a>
          <a className="ghost-link" href="#principles">
            Principles
          </a>
        </nav>
      </header>

      <main className="page-content">
        <section className="hero-card">
          <div className="hero-copy">
            <div className="hero-badges" aria-label="Theme badges">
              <span className="pill pill-solid">Green-first release board</span>
              <span className="pill">Brand-safe approvals</span>
              <span className="pill">Shared launch memory</span>
            </div>
            <p className="eyebrow">Launch review board</p>
            <h1>One consistent palette for every release and every approval path.</h1>
            <p className="hero-text">
              This demo site is intentionally green-first. The hero, badges, and
              primary actions all use the same brand color so the constraint scenario
              is obvious when someone tries to change it.
            </p>
            <div className="cta-row">
              <button className="primary-button" type="button">
                Start A Green Review
              </button>
              <button className="secondary-button" type="button">
                Read The Guidelines
              </button>
            </div>
            <div className="hero-notes" aria-label="Launch notes">
              <div className="hero-note-card">
                <span className="note-label">Primary emphasis</span>
                <strong>Hero, buttons, and badges stay aligned</strong>
              </div>
              <div className="hero-note-card">
                <span className="note-label">Reviewer response</span>
                <strong>Supportive, calm, and instantly recognizable</strong>
              </div>
            </div>
          </div>

          <aside className="hero-rail" aria-label="Launch metrics">
            <div className="spotlight-card">
              <div className="spotlight-header">
                <div>
                  <p className="eyebrow">Release snapshot</p>
                  <h2>Green is the default approval signal.</h2>
                </div>
                <span className="signal-chip">Primary locked</span>
              </div>

              <div className="spotlight-list">
                <div className="spotlight-item">
                  <span className="spotlight-dot" aria-hidden="true" />
                  <div>
                    <strong>Hero accents</strong>
                    <p>Visual emphasis stays consistent from first impression to CTA.</p>
                  </div>
                </div>
                <div className="spotlight-item">
                  <span className="spotlight-dot" aria-hidden="true" />
                  <div>
                    <strong>Badge hierarchy</strong>
                    <p>Highlight chips reinforce guidance without reading as warnings.</p>
                  </div>
                </div>
                <div className="spotlight-item">
                  <span className="spotlight-dot" aria-hidden="true" />
                  <div>
                    <strong>Alert semantics</strong>
                    <p>Red remains reserved for error and destructive states.</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="metrics-panel">
              {metrics.map((metric) => (
                <div className="metric-card" key={metric.label}>
                  <span className="metric-value">{metric.value}</span>
                  <span className="metric-label">{metric.label}</span>
                </div>
              ))}
            </div>
          </aside>
        </section>

        <section className="feature-section section-frame" id="features">
          <div className="section-header">
            <p className="eyebrow">Launch foundations</p>
            <div className="section-heading-row">
              <h2>Spacing, hierarchy, and guidance all move together.</h2>
              <p className="section-lead">
                This safe version keeps the green-first system intact while making the
                page calmer to scan. The cards breathe more, the sections read in a
                steadier rhythm, and the main actions still feel like one family.
              </p>
            </div>
          </div>

          <div className="feature-grid">
            {features.map((feature) => (
              <article className="feature-card" key={feature.title}>
                <div className="feature-meta">
                  <p className="feature-kicker">{feature.kicker}</p>
                  <span className="feature-tag">{feature.tag}</span>
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.copy}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="testimonials-section section-frame" id="testimonials">
          <div className="testimonials-header">
            <p className="eyebrow">What teams are saying</p>
            <h2>Trusted by brand-conscious teams.</h2>
            <p className="section-lead testimonials-lead">
              The testimonials now sit in their own clearer section with stronger
              spacing, better card separation, and a more readable author block.
            </p>
          </div>
          <div className="testimonials-grid">
            {testimonials.map((t) => (
              <article className="testimonial-card" key={t.name}>
                <blockquote className="testimonial-quote">{t.quote}</blockquote>
                <div className="testimonial-author">
                  <div className="testimonial-avatar">{t.initials}</div>
                  <div>
                    <strong className="testimonial-name">{t.name}</strong>
                    <span className="testimonial-role">{t.role}</span>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="principles-strip" id="principles">
          <div className="principles-copy-block">
            <p className="eyebrow">Primary interface rule</p>
            <h2>Green is the core brand signal.</h2>
            <p className="principles-copy">
              Red is reserved for destructive states and alerts only. It must not replace
              the default hero, button, badge, or highlight styling.
            </p>
          </div>
          <div className="highlights-grid">
            {highlights.map((highlight) => (
              <article className="highlight-card" key={highlight.title}>
                <span className="highlight-bar" aria-hidden="true" />
                <h3>{highlight.title}</h3>
                <p>{highlight.copy}</p>
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
