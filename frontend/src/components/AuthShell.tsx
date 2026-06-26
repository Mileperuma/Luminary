import type { ReactNode } from "react";
import { Link } from "react-router-dom";

/** Shared shell for /login and /register — centered card on the cream background. */
export default function AuthShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <main className="min-h-screen bg-cream text-ink px-6 py-12 flex flex-col items-center">
      <Link to="/" className="block mb-10 no-underline" aria-label="Luminary home">
        <div className="inline-flex items-center justify-center w-10 h-10 border border-ink rounded-full">
          <span className="font-serif text-base">L</span>
        </div>
      </Link>

      <section className="w-full max-w-sm bg-card border border-line rounded-lg shadow-soft p-8">
        <h1 className="font-serif text-2xl mb-1">{title}</h1>
        {subtitle && <p className="text-sm text-muted mb-6">{subtitle}</p>}
        {!subtitle && <div className="mb-6" />}
        {children}
      </section>

      {footer && <div className="mt-6 text-sm text-muted">{footer}</div>}
    </main>
  );
}
