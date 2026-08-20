import { Route, Routes } from "react-router-dom";
import LandingPage from "./pages/LandingPage.jsx";
import WorkspacePage from "./pages/WorkspacePage.jsx";
import DatabaseChatPage from "./pages/DatabaseChatPage.jsx";
import PolicyChatPage from "./pages/PolicyChatPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/app" element={<WorkspacePage />} />
      <Route path="/app/database-chat" element={<DatabaseChatPage />} />
      <Route path="/app/policy-chat" element={<PolicyChatPage />} />
    </Routes>
  );
}
