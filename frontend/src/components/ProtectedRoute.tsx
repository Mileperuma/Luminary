import { Navigate, useLocation } from "react-router-dom";
import type { ReactElement } from "react";

import { useAuth } from "../context/AuthContext";

/** Redirects unauthenticated visitors to /login, preserving where they wanted to go. */
export default function ProtectedRoute({ children }: { children: ReactElement }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <main className="min-h-screen bg-cream text-muted flex items-center justify-center">
        <p className="text-sm">Loading…</p>
      </main>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}
