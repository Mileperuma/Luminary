/** API helpers for the feedback endpoint. */

import { api } from "./api";

export type FeedbackKind = "love" | "dislike" | "save" | "skip";

export async function sendFeedback(input: {
  recommendation_id: string;
  kind: FeedbackKind;
}): Promise<void> {
  await api.post("/api/feedback", input);
}
