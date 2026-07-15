/** Shared TypeScript types that mirror the backend's Pydantic schemas. */

export interface UserPublic {
  id: string;
  email: string;
  display_name: string;
  created_at: string;
  last_login_at: string | null;
  onboarding_complete: boolean;
  digest_opt_in: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
  expires_in_minutes: number;
}

export interface ApiError {
  detail: string;
}
