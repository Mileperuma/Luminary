import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

/** Authenticated home page placeholder.
 *
 * Real recommendation tiles (Books / Articles / Movies) land in Sprint 2.
 */
export default function HomePage() {
  const { user, logout } = useAuth();

  return (
    <main className="min-h-screen bg-cream text-ink">
      <header className="border-b border-line px-6 py-3 flex items-center justify-between">
        <Link to="/home" className="font-serif text-lg no-underline">
          Luminary
        </Link>
        <div className="flex items-center gap-4 text-sm text-muted">
          <span>{user?.display_name}</span>
          <button onClick={logout} className="text-ink hover:text-accent">
            Log out
          </button>
        </div>
      </header>

      <section className="max-w-2xl mx-auto px-6 py-16 text-center">
        <h1 className="font-serif text-3xl mb-3">Welcome, {user?.display_name}.</h1>
        <p className="text-muted leading-relaxed mb-8">
          You're signed in. Real recommendations land next sprint — for now this is your home base.
        </p>
        <div className="text-sm text-muted">
          Phase 1 · Sprint 1 of 5 complete.
        </div>
      </section>
    </main>
  );
}
