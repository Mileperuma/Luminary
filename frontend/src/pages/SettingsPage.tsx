import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

import { useAuth } from "../context/AuthContext";
import { api } from "../lib/api";
import { fetchMe } from "../lib/auth";
import { optInToDigest, optOutOfDigest } from "../lib/digest";

interface Preference {
  id: string;
  media_type: "book" | "movie" | "article";
  key: string;
  value: string;
  weight: number;
  source: "chat" | "explicit" | "implicit";
  updated_at: string;
}

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [prefs, setPrefs] = useState<Preference[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [digestOptIn, setDigestOptIn] = useState<boolean>(user?.digest_opt_in ?? false);

  async function toggleDigest() {
    try {
      if (digestOptIn) {
        await optOutOfDigest();
        setDigestOptIn(false);
      } else {
        await optInToDigest();
        setDigestOptIn(true);
      }
      // Refresh cached profile so the header shows the right state.
      await fetchMe().catch(() => undefined);
    } catch {
      setError("Could not update your digest preference.");
    }
  }

  async function reload() {
    setLoading(true);
    try {
      const res = await api.get<Preference[]>("/api/preferences");
      setPrefs(res.data);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setError(String(err.response.data.detail));
      } else {
        setError("Could not load your preferences.");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void reload();
  }, []);

  async function remove(id: string) {
    try {
      await api.delete(`/api/preferences/${id}`);
      setPrefs((p) => p.filter((x) => x.id !== id));
    } catch {
      setError("Could not delete that preference.");
    }
  }

  return (
    <main className="min-h-screen bg-cream text-ink">
      <header className="border-b border-line px-6 py-3 flex items-center justify-between">
        <Link to="/home" className="font-serif text-lg no-underline">
          Luminary
        </Link>
        <div className="flex items-center gap-4 text-sm text-muted">
          <span>{user?.display_name}</span>
          <button onClick={() => { logout(); navigate("/"); }} className="text-ink hover:text-accent">
            Log out
          </button>
        </div>
      </header>

      <section className="max-w-3xl mx-auto px-6 py-10">
        <Link to="/home" className="text-sm text-muted no-underline hover:text-ink">
          ← Back to home
        </Link>
        <h1 className="font-serif text-3xl mb-2 mt-4">Your preferences</h1>
        <p className="text-muted mb-6">
          These are the taste signals Luminary uses to pick for you. Delete what's wrong.
        </p>

        <div className="mb-8 p-4 border border-line rounded-lg bg-card flex items-center justify-between">
          <div>
            <p className="font-medium">Weekly digest email</p>
            <p className="text-sm text-muted">
              One personalised summary of your picks, every Sunday.
            </p>
          </div>
          <button
            onClick={toggleDigest}
            aria-pressed={digestOptIn}
            className={
              "px-4 py-2 rounded-lg text-sm font-medium border transition-colors " +
              (digestOptIn
                ? "bg-ink text-cream border-ink"
                : "bg-transparent text-ink border-line hover:border-ink")
            }
          >
            {digestOptIn ? "Subscribed" : "Subscribe"}
          </button>
        </div>

        {error && (
          <p role="alert" className="text-sm text-ink bg-line/40 rounded-md px-3 py-2 mb-4">
            {error}
          </p>
        )}

        {loading && <p className="text-muted">Loading…</p>}

        {!loading && prefs.length === 0 && (
          <div className="border border-line rounded-lg p-6 bg-card">
            <p className="text-muted mb-3">
              No preferences saved yet. Try the onboarding chat to set up your profile.
            </p>
            <Link
              to="/onboarding"
              className="text-ink no-underline border-b border-ink hover:text-accent hover:border-accent"
            >
              Start onboarding chat
            </Link>
          </div>
        )}

        {!loading && prefs.length > 0 && (
          <ul className="list-none p-0 space-y-2">
            {prefs.map((p) => (
              <li
                key={p.id}
                className="bg-card border border-line rounded-lg p-3 flex items-center justify-between"
              >
                <div>
                  <p className="text-xs uppercase tracking-wide text-muted">
                    {p.media_type} · {p.key} · weight {p.weight.toFixed(1)}
                  </p>
                  <p className="text-ink">{p.value}</p>
                </div>
                <button
                  onClick={() => remove(p.id)}
                  className="text-sm text-muted hover:text-ink"
                  aria-label={`Delete preference: ${p.value}`}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
