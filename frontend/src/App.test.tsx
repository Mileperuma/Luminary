import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import App from "./App";
import { AuthProvider } from "./context/AuthContext";

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe("App routing", () => {
  it("renders the landing page at /", () => {
    renderAt("/");
    expect(screen.getByRole("heading", { name: "Luminary" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /create an account/i })).toBeInTheDocument();
  });

  it("renders the login page at /login", () => {
    renderAt("/login");
    expect(screen.getByRole("heading", { name: /welcome back/i })).toBeInTheDocument();
  });

  it("renders the register page at /register", () => {
    renderAt("/register");
    expect(screen.getByRole("heading", { name: /create your luminary/i })).toBeInTheDocument();
  });

  it("redirects /home to /login when unauthenticated", () => {
    renderAt("/home");
    // ProtectedRoute will redirect → login screen renders
    expect(screen.getByRole("heading", { name: /welcome back/i })).toBeInTheDocument();
  });
});
