import { useEffect, useState } from "react";

export type Mood = "light" | "intense" | "contemplative" | "fun" | "dark";

const MOODS: { value: Mood; label: string; description: string }[] = [
  { value: "light", label: "Light", description: "Easy, hopeful, low stakes." },
  { value: "intense", label: "Intense", description: "Big stakes, fast pulse." },
  { value: "contemplative", label: "Contemplative", description: "Quiet, thoughtful, slow." },
  { value: "fun", label: "Fun", description: "Playful, sharp, entertaining." },
  { value: "dark", label: "Dark", description: "Heavier themes, morally complex." },
];

const STORAGE_KEY = "luminary.mood";

interface Props {
  onChange?: (mood: Mood | null) => void;
}

/** Mood pill row, also persists the active mood across page reloads. */
export default function MoodSelector({ onChange }: Props) {
  const [mood, setMood] = useState<Mood | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY) as Mood | null;
    if (stored && MOODS.some((m) => m.value === stored)) {
      setMood(stored);
      onChange?.(stored);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function toggle(value: Mood) {
    const next: Mood | null = mood === value ? null : value;
    setMood(next);
    if (next) {
      localStorage.setItem(STORAGE_KEY, next);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
    onChange?.(next);
  }

  return (
    <div role="group" aria-label="Choose a mood" className="mb-8">
      <p className="text-sm text-muted text-center mb-3">
        I'm in the mood for…
      </p>
      <div className="flex flex-wrap gap-2 justify-center">
        {MOODS.map(({ value, label, description }) => (
          <button
            key={value}
            type="button"
            onClick={() => toggle(value)}
            aria-pressed={mood === value}
            title={description}
            className={
              "px-3 py-1.5 rounded-full border text-sm transition-colors " +
              (mood === value
                ? "border-ink bg-ink text-cream"
                : "border-line text-ink hover:border-ink")
            }
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}

export function readPersistedMood(): Mood | null {
  if (typeof localStorage === "undefined") return null;
  const stored = localStorage.getItem(STORAGE_KEY) as Mood | null;
  return stored && MOODS.some((m) => m.value === stored) ? stored : null;
}
