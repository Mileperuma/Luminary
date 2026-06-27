/** API helpers for the recommendation endpoints. */

import { api } from "./api";

export type MediaType = "book" | "movie" | "article";

export interface SimilarItem {
  media_type: MediaType;
  external_id: string;
  title: string;
  description: string;
  image_url: string | null;
  trailer_url: string | null;
  keywords: string[];
}

export interface Recommendation {
  id: string;
  media_type: MediaType;
  external_id: string;
  title: string;
  image_url: string | null;
  trailer_url: string | null;
  description: string;
  similar_items: SimilarItem[];
  created_at: string;
}

export async function getRecommendation(input: {
  media_type: MediaType;
  mood?: string;
}): Promise<Recommendation> {
  const res = await api.post<Recommendation>("/api/recommendations", input);
  return res.data;
}
