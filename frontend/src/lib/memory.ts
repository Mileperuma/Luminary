/** API helpers for /api/memory/welcome. */

import { api } from "./api";

export interface FreshPick {
  id: string;
  media_type: "book" | "movie" | "article";
  title: string;
  image_url: string | null;
  trailer_url: string | null;
  description: string;
}

export interface WelcomePayload {
  greeting: string;
  is_returning: boolean;
  needs_onboarding: boolean;
  fresh_picks: FreshPick[];
}

export async function fetchWelcome(): Promise<WelcomePayload> {
  const res = await api.get<WelcomePayload>("/api/memory/welcome");
  return res.data;
}
