import type { SimilarItem } from "../lib/recommendations";

interface Props {
  items: SimilarItem[];
}

/** Row of similar items shown beneath the primary recommendation. */
export default function SimilarStrip({ items }: Props) {
  if (!items.length) return null;
  return (
    <section className="mt-8">
      <h3 className="text-sm font-medium text-muted mb-3">Similar to this</h3>
      <ul className="grid grid-cols-2 md:grid-cols-4 gap-4 list-none p-0">
        {items.map((item) => (
          <li
            key={item.external_id}
            className="bg-card border border-line rounded-lg p-3 flex flex-col"
          >
            <div className="aspect-[2/3] bg-line/30 rounded mb-2 overflow-hidden">
              {item.image_url ? (
                <img
                  src={item.image_url}
                  alt={`Cover of ${item.title}`}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-muted text-xs">
                  No cover
                </div>
              )}
            </div>
            <p className="text-sm font-medium leading-snug">{item.title}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
