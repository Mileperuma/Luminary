/** Digest opt-in / opt-out helpers. */

import { api } from "./api";

export async function optInToDigest(): Promise<void> {
  await api.post("/api/digest/opt-in");
}

export async function optOutOfDigest(): Promise<void> {
  await api.post("/api/digest/opt-out");
}
