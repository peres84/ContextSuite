const metrics = [
  { label: "Teams onboarded", value: "24" },
  { label: "Weekly reviews", value: "138" },
  { label: "Green-safe releases", value: "99.2%" },
];

const features = [
  {
    title: "Constraint-aware review",
    copy: "Every launch checklist, brand rule, and approval note stays close to the work.",
  },
  {
    title: "Calm operator workflow",
    copy: "One page for approvals, one tone of voice, and one obvious primary action.",
  },
  {
    title: "Reusable design memory",
    copy: "Patterns that worked before become guidance for the next team and the next release.",
  },
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
            <h1>Keep the brand calm, clear, and unmistakably green.</h1>
          </div>
        </div>
        <a className="ghost-link" href="#features">
          View principles
        </a>
      </header>

      <main>
        <section className="hero-card">
          <div className="hero-copy">
            <p className="eyebrow">Launch review board</p>
            <h2>One consistent palette for every release and every approval path.</h2>
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
          </div>

          <aside className="metrics-panel" aria-label="Launch metrics">
            {metrics.map((metric) => (
              <div className="metric-card" key={metric.label}>
                <span className="metric-value">{metric.value}</span>
                <span className="metric-label">{metric.label}</span>
              </div>
            ))}
          </aside>
        </section>

        <section className="feature-grid" id="features">
          {features.map((feature) => (
            <article className="feature-card" key={feature.title}>
              <p className="feature-kicker">Green rule</p>
              <h3>{feature.title}</h3>
              <p>{feature.copy}</p>
            </article>
          ))}
        </section>

        <section className="principles-strip">
          <div>
            <p className="eyebrow">Primary interface rule</p>
            <h3>Green is the core brand signal.</h3>
          </div>
          <p className="principles-copy">
            Red is reserved for destructive states and alerts only. It must not replace
            the default hero, button, badge, or highlight styling.
          </p>
        </section>
      </main>
    </div>
  );
}
