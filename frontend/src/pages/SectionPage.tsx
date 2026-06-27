import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

import Button from "../components/Button";
import FeedbackBar from "../components/FeedbackBar";
import RecommendationCard from "../components/RecommendationCard";
import SimilarStrip from "../components/SimilarStrip";
import { useAuth } from "../context/AuthContext";
import { getRecommendation } from "../lib/recommendations";
import type { MediaType, Recommendation } from "../lib/recommendations";

interface Props {
  mediaType: MediaType;
  heading: string;
  subline: string;
}

/** Generic section page used by /books, /articles, /movies. */
export default function SectionPage({ mediaType, heading, subline }: Props) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [rec, setRec] = useState<Recommendation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchPick() {
    setLoading(true);
    setError(null);
    try {
      const r = await getRecommendation({ media_type: mediaType });
      setRec(r);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setError(String(err.response.data.detail));
      } else {
        setError("Could not get a pick right now. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void fetchPick();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mediaType]);

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

      <section className="max-w-4xl mx-auto px-6 py-10">
        <Link to="/home" className="text-sm text-muted no-underline hover:text-ink">
          ← Back to home
        </Link>
        <h1 className="font-serif text-3xl mb-2 mt-4">{heading}</h1>
        <p className="text-muted mb-8">{subline}</p>

        <div className="mb-6 max-w-xs">
          <Button onClick={fetchPick} loading={loading} variant="ghost">
            Show me another
          </Button>
        </div>

        {error && (
          <p role="alert" className="text-sm text-ink bg-line/40 rounded-md px-3 py-2 mb-4">
            {error}
          </p>
        )}

        {rec && (
          <>
            <RecommendationCard recommendation={rec} />
            <FeedbackBar recommendationId={rec.id} onSkip={fetchPick} />
            <SimilarStrip items={rec.similar_items} />
          </>
        )}

        {!rec && !loading && !error && (
          <p className="text-muted">Loading your first pick…</p>
        )}
      </section>
    </main>
  );
}
