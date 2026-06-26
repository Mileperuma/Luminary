import { Link } from "react-router-dom";

/** Public landing page — shown to unauthenticated visitors at /. */
export default function LandingPage() {
  return (
    <main className="min-h-screen bg-cream text-ink px-6 flex items-center justify-center">
      <div className="max-w-xl text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 mb-6 border border-ink rounded-full">
          <span className="font-serif text-xl">L</span>
        </div>

        <h1 className="font-serif text-4xl mb-3">Luminary</h1>
        <p className="text-muted text-lg leading-relaxed mb-8">
          An AI-powered assistant that learns your taste in books, articles, and movies —
          and gets a little smarter every visit.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            to="/register"
            className="px-5 py-2 rounded-lg bg-ink text-cream text-sm font-medium no-underline hover:bg-ink/90"
          >
            Create an account
          </Link>
          <Link
            to="/login"
            className="px-5 py-2 rounded-lg border border-line text-ink text-sm font-medium no-underline hover:border-ink"
          >
            Log in
          </Link>
        </div>
      </div>
    </main>
  );
}
