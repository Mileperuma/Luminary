/** API helpers for the auth endpoints — thin typed wrappers around axios. */

import { api, setToken } from "./api";
import type { TokenResponse, UserPublic } from "./types";

export async function register(input: {
  email: string;
  password: string;
  display_name: string;
}): Promise<UserPublic> {
  const res = await api.post<UserPublic>("/api/auth/register", input);
  return res.data;
}

export async function login(input: {
  email: string;
  password: string;
}): Promise<TokenResponse> {
  const res = await api.post<TokenResponse>("/api/auth/login", input);
  setToken(res.data.access_token);
  return res.data;
}

export async function fetchMe(): Promise<UserPublic> {
  const res = await api.get<UserPublic>("/api/auth/me");
  return res.data;
}

export function logout(): void {
  setToken(null);
}
