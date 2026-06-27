import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

const SECTIONS = [
  { label: "Books", path: "/books", description: "One pick + four close reads." },
  { label: "Articles", path: "/articles", description: "Smart long-form on your wavelength." },
  { label: "Movies", path: "/movies", description: "Pick + trailer + similar films." },
];

export default function HomePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

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
        <h1 className="font-serif text-3xl mb-2 text-center">
          Welcome, {user?.display_name}.
        </h1>
        <p className="text-muted text-center mb-12">What are you in the mood for?</p>

        {user && !user.onboarding_complete && (
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
