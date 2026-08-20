import { Route, Routes } from "react-router-dom";
import LandingPage from "./pages/LandingPage.jsx";
import WorkspacePage from "./pages/WorkspacePage.jsx";
import DatabaseChatPage from "./pages/DatabaseChatPage.jsx";
import PolicyChatPage from "./pages/PolicyChatPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";
import ActivityPage from "./pages/ActivityPage.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import { RequireAuth } from "./components/RequireAuth.jsx";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/app"
          element={
            <RequireAuth>
              <WorkspacePage />
            </RequireAuth>
          }
        />
        <Route
          path="/app/database-chat"
          element={
            <RequireAuth>
              <DatabaseChatPage />
            </RequireAuth>
          }
        />
        <Route
          path="/app/policy-chat"
          element={
            <RequireAuth>
              <PolicyChatPage />
            </RequireAuth>
          }
        />
        <Route
          path="/app/activity"
          element={
            <RequireAuth adminOnly>
              <ActivityPage />
            </RequireAuth>
          }
        />
      </Routes>
    </AuthProvider>
  );
}
