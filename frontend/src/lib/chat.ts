/** API helpers for the chat endpoints. */

import { api } from "./api";

export type ChatSessionType = "onboarding" | "general";

export interface StartChatResponse {
  session_id: string;
  opening_message: string;
}

export interface ChatMessageResponse {
  session_id: string;
  assistant_message: string;
  finished: boolean;
  captured_preferences: number;
}

export async function startChat(sessionType: ChatSessionType): Promise<StartChatResponse> {
  const res = await api.post<StartChatResponse>("/api/chat/start", {
    session_type: sessionType,
  });
  return res.data;
}

export async function sendChatMessage(input: {
  session_id: string;
  content: string;
}): Promise<ChatMessageResponse> {
  const res = await api.post<ChatMessageResponse>("/api/chat/message", input);
  return res.data;
}
