import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders the project name", () => {
    render(<App />);
    expect(screen.getByText("Luminary")).toBeInTheDocument();
  });

  it("explains the scaffold state", () => {
    render(<App />);
    expect(screen.getByText(/Phase 0 — scaffold up/i)).toBeInTheDocument();
  });
});
