/** API helper for the cross-media endpoint. */

import { api } from "./api";
import type { SimilarItem } from "./recommendations";

export type CrossMediaResponse = Partial<Record<"book" | "movie" | "article", SimilarItem>>;

export async function fetchCrossMedia(recommendationId: string): Promise<CrossMediaResponse> {
  const res = await api.get<CrossMediaResponse>(`/api/recommendations/${recommendationId}/cross-media`);
  return res.data;
}
