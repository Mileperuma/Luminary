import { useEffect, useState } from "react";

import { fetchCrossMedia } from "../lib/crossMedia";
import type { CrossMediaResponse } from "../lib/crossMedia";

interface Props {
  recommendationId: string;
}

const MEDIA_LABELS: Record<string, string> = {
  book: "Related book",
  movie: "Related film",
  article: "Related article",
};

/** "If you loved this book, here's the film and a long-read article…" */
export default function CrossMediaStrip({ recommendationId }: Props) {
  const [data, setData] = useState<CrossMediaResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setData(null);
    fetchCrossMedia(recommendationId)
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch(() => {
        if (!cancelled) setData({});
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [recommendationId]);

  if (loading) return null;
  if (!data) return null;
  const entries = Object.entries(data) as Array<[keyof CrossMediaResponse, NonNullable<CrossMediaResponse[keyof CrossMediaResponse]>]>;
  if (entries.length === 0) return null;

  return (
    <section className="mt-8" aria-label="Cross-media suggestions">
      <h3 className="text-sm font-medium text-muted mb-3">
        Across media
      </h3>
      <ul className="grid grid-cols-1 md:grid-cols-2 gap-4 list-none p-0">
        {entries.map(([mediaType, item]) => (
          <li
            key={mediaType}
            className="bg-card border border-line rounded-lg p-3 flex gap-3"
          >
            <div className="w-20 aspect-[2/3] bg-line/30 rounded overflow-hidden shrink-0">
              {item.image_url ? (
                <img
                  src={item.image_url}
                  alt={`Cover of ${item.title}`}
                  className="w-full h-full object-cover"
                />
              ) : null}
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-muted">
                {MEDIA_LABELS[mediaType] ?? mediaType}
              </p>
              <p className="font-medium text-sm leading-snug">{item.title}</p>
              {item.description && (
                <p className="text-xs text-muted mt-1 line-clamp-3">{item.description}</p>
              )}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
