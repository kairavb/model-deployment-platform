import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/layout/AppLayout";
import { ProtectedRoute } from "./components/shared/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import { DashboardPage } from "./pages/Dashboard";
import { DeploymentDetailPage } from "./pages/DeploymentDetail";
import { DeploymentsPage } from "./pages/Deployments";
import { LoginPage } from "./pages/Login";
import { ModelDetailPage } from "./pages/ModelDetail";
import { ModelsPage } from "./pages/Models";
import { AnalyticsPage } from "./pages/Analytics";
import { ApiKeysPage } from "./pages/ApiKeys";
import { PlaygroundPage } from "./pages/Playground";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/models" element={<ModelsPage />} />
            <Route path="/models/:modelId" element={<ModelDetailPage />} />
            <Route path="/deployments" element={<DeploymentsPage />} />
            <Route path="/deployments/:deploymentId" element={<DeploymentDetailPage />} />
            <Route path="/playground" element={<PlaygroundPage />} />
            <Route path="/deployments/:deploymentId/playground" element={<PlaygroundPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/api-keys" element={<ApiKeysPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
