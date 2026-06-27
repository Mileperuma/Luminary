import type { Recommendation } from "../lib/recommendations";

interface Props {
  recommendation: Recommendation;
}

/** Primary recommendation card — image + title + LLM-written explanation
 *  + embedded trailer for movies. */
export default function RecommendationCard({ recommendation }: Props) {
  const { title, image_url, description, trailer_url, media_type } = recommendation;
  return (
    <article className="bg-card border border-line rounded-lg shadow-soft overflow-hidden">
      <div className="md:flex">
        <div className="md:w-1/3 bg-line/30 flex items-center justify-center">
          {image_url ? (
            <img src={image_url} alt={`Cover of ${title}`} className="w-full h-full object-cover" />
          ) : (
            <span className="text-muted text-sm py-16">No cover</span>
          )}
        </div>
        <div className="md:w-2/3 p-6">
          <p className="text-xs uppercase tracking-wide text-muted mb-1">Your Pick</p>
          <h2 className="font-serif text-2xl mb-2">{title}</h2>
          <p className="text-sm text-muted mb-2">Why we picked this</p>
          <p className="text-ink leading-relaxed mb-4">{description}</p>

          {media_type === "movie" && trailer_url && (
            <div className="aspect-video w-full rounded-md overflow-hidden border border-line">
              <iframe
                src={trailer_url}
                title={`Trailer for ${title}`}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="w-full h-full"
                sandbox="allow-scripts allow-same-origin allow-presentation"
              />
            </div>
          )}
        </div>
      </div>
    </article>
  );
}
