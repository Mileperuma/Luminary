/** Lightweight accessibility checks on the public-facing pages.
 *
 * Uses axe-core via @testing-library/react. These tests will fail the build
 * if any of the screens introduces WCAG AA violations.
 */

import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import axe from "axe-core";
import { afterEach, describe, expect, it } from "vitest";

import App from "../App";
import { AuthProvider } from "../context/AuthContext";

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </MemoryRouter>,
  );
}

async function runAxe(): Promise<axe.AxeResults> {
  return axe.run(document.body, {
    runOnly: { type: "tag", values: ["wcag2a", "wcag2aa"] },
  });
}

afterEach(() => {
  // Reset the document between tests so axe sees only the current render.
  document.body.innerHTML = "";
});

describe("accessibility — public pages", () => {
  it("landing page has no WCAG AA violations", async () => {
    renderAt("/");
    const results = await runAxe();
    expect(results.violations).toEqual([]);
  });

  it("login page has no WCAG AA violations", async () => {
    renderAt("/login");
    const results = await runAxe();
    expect(results.violations).toEqual([]);
  });

  it("register page has no WCAG AA violations", async () => {
    renderAt("/register");
    const results = await runAxe();
    expect(results.violations).toEqual([]);
  });
});
