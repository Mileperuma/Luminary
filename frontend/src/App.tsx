import { Navigate, Route, Routes } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import HomePage from "./pages/HomePage";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import OnboardingPage from "./pages/OnboardingPage";
import RegisterPage from "./pages/RegisterPage";
import SectionPage from "./pages/SectionPage";
import SettingsPage from "./pages/SettingsPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/home"
        element={
          <ProtectedRoute>
            <HomePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/onboarding"
        element={
          <ProtectedRoute>
            <OnboardingPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/books"
        element={
          <ProtectedRoute>
            <SectionPage
              mediaType="book"
              heading="Books"
              subline="Tell me what to read next."
            />
          </ProtectedRoute>
        }
      />
      <Route
        path="/articles"
        element={
          <ProtectedRoute>
            <SectionPage
              mediaType="article"
              heading="Articles"
              subline="A long read worth your time."
            />
          </ProtectedRoute>
        }
      />
      <Route
        path="/movies"
        element={
          <ProtectedRoute>
            <SectionPage
              mediaType="movie"
              heading="Movies"
              subline="One pick with a trailer."
            />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
