import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";

import { fetchMe, login as apiLogin, logout as apiLogout, register as apiRegister } from "../lib/auth";
import { getToken } from "../lib/api";
import type { UserPublic } from "../lib/types";

interface AuthState {
  user: UserPublic | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, display_name: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserPublic | null>(null);
  const [loading, setLoading] = useState(true);

  // On mount, if there's a stored token, fetch /me to confirm it's still valid.
  useEffect(() => {
    let cancelled = false;
    async function bootstrap() {
      if (!getToken()) {
        setLoading(false);
        return;
      }
      try {
        const me = await fetchMe();
        if (!cancelled) setUser(me);
      } catch {
        // 401 — interceptor already cleared the token
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  async function login(email: string, password: string) {
    await apiLogin({ email, password });
    const me = await fetchMe();
    setUser(me);
  }

  async function register(email: string, password: string, display_name: string) {
    await apiRegister({ email, password, display_name });
    await login(email, password);
  }

  function logout() {
    apiLogout();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
