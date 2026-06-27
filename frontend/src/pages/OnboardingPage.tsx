import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import ChatPanel from "../components/ChatPanel";
import { useAuth } from "../context/AuthContext";

export default function OnboardingPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [done, setDone] = useState(false);
  const [capturedCount, setCapturedCount] = useState(0);

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

      <section className="max-w-2xl mx-auto px-6 py-10">
        <h1 className="font-serif text-3xl mb-2">Let's tune your picks.</h1>
        <p className="text-muted mb-6">
          A short chat — under five minutes. No wrong answers; you can edit anything later.
        </p>

        <ChatPanel
          sessionType="onboarding"
          onFinished={(captured) => {
            setDone(true);
            setCapturedCount(captured);
          }}
        />

        {done && (
          <div className="mt-6 p-4 border border-line rounded-lg bg-card">
            <p className="mb-3">
              Saved {capturedCount} {capturedCount === 1 ? "preference" : "preferences"}. You're all set.
            </p>
            <button
              onClick={() => navigate("/home")}
              className="px-4 py-2 rounded-lg bg-ink text-cream text-sm font-medium hover:bg-ink/90"
            >
              See my picks
            </button>
          </div>
        )}
      </section>
    </main>
  );
}
