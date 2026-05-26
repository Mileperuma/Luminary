/**
 * Placeholder landing screen for Phase 0 (scaffold only).
 *
 * Real screens land in Sprint 1+ — see docs/03_Project_Plan.docx Section 5.2.
 */
export default function App() {
  return (
    <main className="min-h-screen bg-cream text-ink flex items-center justify-center px-6">
      <div className="max-w-xl text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 mb-6 border border-ink rounded-full">
          <span className="font-serif text-xl">L</span>
        </div>

        <h1 className="font-serif text-4xl mb-3">Luminary</h1>
        <p className="text-muted text-lg leading-relaxed mb-8">
          An AI-powered assistant that learns your taste in books, articles, and movies —
          and gets a little smarter every visit.
        </p>

        <p className="text-sm text-muted">
          Phase 0 — scaffold up. Feature screens land in Sprint 1.
        </p>
      </div>
    </main>
  );
}
