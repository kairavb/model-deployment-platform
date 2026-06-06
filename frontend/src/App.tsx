import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/layout/AppLayout";
import { DashboardPage } from "./pages/Dashboard";
import { DeploymentDetailPage } from "./pages/DeploymentDetail";
import { DeploymentsPage } from "./pages/Deployments";
import { LoginPage } from "./pages/Login";
import { ModelDetailPage } from "./pages/ModelDetail";
import { ModelsPage } from "./pages/Models";
import { PlaygroundPage } from "./pages/Playground";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/models" element={<ModelsPage />} />
        <Route path="/models/:modelId" element={<ModelDetailPage />} />
        <Route path="/deployments" element={<DeploymentsPage />} />
        <Route path="/deployments/:deploymentId" element={<DeploymentDetailPage />} />
        <Route path="/deployments/:deploymentId/playground" element={<PlaygroundPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
