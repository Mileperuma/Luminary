import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { fetchWelcome } from "../lib/memory";
import type { WelcomePayload } from "../lib/memory";

const SECTIONS = [
  { label: "Books", path: "/books", description: "One pick + four close reads." },
  { label: "Articles", path: "/articles", description: "Smart long-form on your wavelength." },
  { label: "Movies", path: "/movies", description: "Pick + trailer + similar films." },
];

const MEDIA_TO_PATH: Record<string, string> = {
  book: "/books",
  movie: "/movies",
  article: "/articles",
};

export default function HomePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [welcome, setWelcome] = useState<WelcomePayload | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await fetchWelcome();
        if (!cancelled) setWelcome(data);
      } catch {
        // Non-fatal — fall back to the static greeting below.
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  const greeting = welcome?.greeting ?? `Welcome, ${user?.display_name}.`;
  const needsOnboarding = welcome?.needs_onboarding ?? !user?.onboarding_complete;
  const freshPicks = welcome?.fresh_picks ?? [];

  return (
    <main className="min-h-screen bg-cream text-ink">
      <header className="border-b border-line px-6 py-3 flex items-center justify-between">
        <Link to="/home" className="font-serif text-lg no-underline">
          Luminary
        </Link>
        <nav className="flex items-center gap-4 text-sm text-muted">
          <Link to="/settings" className="text-ink no-underline hover:text-accent">
            Preferences
          </Link>
          <span>{user?.display_name}</span>
          <button onClick={() => { logout(); navigate("/"); }} className="text-ink hover:text-accent">
            Log out
          </button>
        </nav>
      </header>

      <section className="max-w-3xl mx-auto px-6 py-16">
        <h1 className="font-serif text-3xl mb-2 text-center">{greeting}</h1>
        <p className="text-muted text-center mb-12">What are you in the mood for?</p>

        {needsOnboarding && (
          <div className="mb-10 p-4 border border-line rounded-lg bg-card flex items-center justify-between">
            <div>
              <p className="font-medium">Tell Luminary what you like.</p>
              <p className="text-sm text-muted">A short chat — under five minutes.</p>
            </div>
            <Link
              to="/onboarding"
              className="px-4 py-2 rounded-lg bg-ink text-cream text-sm font-medium no-underline hover:bg-ink/90"
            >
              Start chat
            </Link>
          </div>
        )}

        {freshPicks.length > 0 && (
          <section className="mb-12">
            <h2 className="text-sm uppercase tracking-wide text-muted mb-3">Recent picks</h2>
            <ul className="grid md:grid-cols-3 gap-4 list-none p-0">
              {freshPicks.map((pick) => (
                <li key={pick.id}>
                  <Link
                    to={MEDIA_TO_PATH[pick.media_type] ?? "/home"}
                    className="block bg-card border border-line rounded-lg overflow-hidden no-underline text-ink hover:border-ink"
                  >
                    {pick.image_url ? (
                      <img src={pick.image_url} alt="" className="w-full aspect-video object-cover" />
                    ) : (
                      <div className="w-full aspect-video bg-line/30" />
                    )}
                    <div className="p-3">
                      <p className="text-xs uppercase tracking-wide text-muted">
                        {pick.media_type}
                      </p>
                      <p className="font-medium text-sm">{pick.title}</p>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        )}

        <ul className="grid md:grid-cols-3 gap-4 list-none p-0">
          {SECTIONS.map(({ label, path, description }) => (
            <li key={path}>
              <Link
                to={path}
                className="block p-6 bg-card border border-line rounded-lg shadow-soft no-underline text-ink hover:border-ink transition-colors"
              >
                <h2 className="font-serif text-xl mb-2">{label}</h2>
                <p className="text-sm text-muted">{description}</p>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
