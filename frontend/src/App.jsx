import { Route, Routes } from "react-router-dom";
import LandingPage from "./pages/LandingPage.jsx";
import WorkspacePage from "./pages/WorkspacePage.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/app" element={<WorkspacePage />} />
    </Routes>
  );
}
