import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

import AuthShell from "../components/AuthShell";
import Button from "../components/Button";
import TextField from "../components/TextField";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register(email, password, displayName);
      navigate("/home", { replace: true });
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setError(String(err.response.data.detail));
      } else {
        setError("Could not create your account. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthShell
      title="Create your Luminary"
      subtitle="One taste profile, three sections, calm by default."
      footer={
        <>
          Already have an account?{" "}
          <Link to="/login" className="text-accent">
            Log in
          </Link>
        </>
      }
    >
      <form onSubmit={onSubmit} noValidate>
        <TextField
          label="Your name"
          type="text"
          autoComplete="name"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          required
        />
        <TextField
          label="Email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <TextField
          label="Password"
          type="password"
          autoComplete="new-password"
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && (
          <p role="alert" className="text-sm text-ink bg-line/40 rounded-md px-3 py-2 mb-4">
            {error}
          </p>
        )}
        <Button type="submit" loading={submitting}>
          Create account
        </Button>
      </form>
    </AuthShell>
  );
}
