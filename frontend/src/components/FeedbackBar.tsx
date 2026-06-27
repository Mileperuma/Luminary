import { useState } from "react";

import { sendFeedback } from "../lib/feedback";
import type { FeedbackKind } from "../lib/feedback";

interface Props {
  recommendationId: string;
  onSkip?: () => void;
}

const ACTIONS: { kind: FeedbackKind; label: string; ariaLabel: string }[] = [
  { kind: "love", label: "Love it", ariaLabel: "Mark recommendation as loved" },
  { kind: "dislike", label: "Not for me", ariaLabel: "Mark recommendation as not for me" },
  { kind: "save", label: "Save", ariaLabel: "Save this recommendation for later" },
];

/** Four-button feedback bar shown beneath a recommendation card. */
export default function FeedbackBar({ recommendationId, onSkip }: Props) {
  const [submitted, setSubmitted] = useState<FeedbackKind | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit(kind: FeedbackKind) {
    setError(null);
    try {
      await sendFeedback({ recommendation_id: recommendationId, kind });
      setSubmitted(kind);
      if (kind === "skip") onSkip?.();
    } catch {
      setError("Could not save that. Try again.");
    }
  }

  return (
    <div
      className="mt-6 bg-card border border-line rounded-lg p-4"
      role="group"
      aria-label="Recommendation feedback"
    >
      <p className="text-sm font-medium mb-3">Was this a good pick?</p>
      <div className="flex flex-wrap gap-2">
        {ACTIONS.map(({ kind, label, ariaLabel }) => (
          <button
            key={kind}
            onClick={() => submit(kind)}
            disabled={submitted !== null}
            aria-label={ariaLabel}
            aria-pressed={submitted === kind}
            className={
              "px-3 py-1.5 rounded-md border text-sm transition-colors " +
              (submitted === kind
                ? "border-ink bg-ink text-cream"
                : "border-line text-ink hover:border-ink") +
              " disabled:opacity-50"
            }
          >
            {label}
          </button>
        ))}
        <button
          onClick={() => submit("skip")}
          disabled={submitted !== null}
          aria-label="Show me another recommendation"
          className="px-3 py-1.5 rounded-md border border-line text-ink text-sm hover:border-ink disabled:opacity-50"
        >
          Show another
        </button>
      </div>

      {error && (
        <p role="alert" className="text-xs text-ink bg-line/40 mt-3 px-2 py-1 rounded">
          {error}
        </p>
      )}
      {submitted && submitted !== "skip" && (
        <p className="text-xs text-muted mt-3">Thanks — that helps tune future picks.</p>
      )}
    </div>
  );
}
