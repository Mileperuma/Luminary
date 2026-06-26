import type { InputHTMLAttributes } from "react";

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

let _id = 0;
function nextId(): string {
  _id += 1;
  return `field-${_id}`;
}

/** Labelled, accessible input that fits the calm light theme. */
export default function TextField({ label, error, id, ...rest }: TextFieldProps) {
  const realId = id ?? nextId();
  return (
    <div className="mb-4">
      <label htmlFor={realId} className="block text-sm font-medium mb-1">
        {label}
      </label>
      <input
        id={realId}
        className="w-full px-3 py-2 bg-card text-ink border border-line rounded-lg
                   focus:border-accent focus:ring-1 focus:ring-accent outline-none
                   placeholder:text-muted/70"
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${realId}-error` : undefined}
        {...rest}
      />
      {error && (
        <p id={`${realId}-error`} className="mt-1 text-xs text-ink">
          {error}
        </p>
      )}
    </div>
  );
}
