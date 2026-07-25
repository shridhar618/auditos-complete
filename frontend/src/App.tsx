import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { AuthProvider } from "@/context/AuthContext";
import { ThemeProvider } from "@/context/ThemeContext";
import ComingSoonPage from "@/pages/ComingSoonPage";
import AiAgentsPage from "@/pages/AiAgentsPage";
import AnalyticsPage from "@/pages/AnalyticsPage";
import DashboardPage from "@/pages/DashboardPage";
import DocumentsPage from "@/pages/DocumentsPage";
import InvestigationDetailPage from "@/pages/InvestigationDetailPage";
import InvestigationsPage from "@/pages/InvestigationsPage";
import LoginPage from "@/pages/LoginPage";
import NotFoundPage from "@/pages/NotFoundPage";
import PolicyCenterPage from "@/pages/PolicyCenterPage";
import RegisterPage from "@/pages/RegisterPage";
import ReportsPage from "@/pages/ReportsPage";
import TransactionDetailPage from "@/pages/TransactionDetailPage";
import TransactionsPage from "@/pages/TransactionsPage";
import ProtectedRoute from "@/routes/ProtectedRoute";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              <Route element={<ProtectedRoute />}>
                <Route element={<AppShell />}>
                  <Route index element={<DashboardPage />} />
                  <Route path="/transactions" element={<TransactionsPage />} />
                  <Route path="/transactions/:id" element={<TransactionDetailPage />} />
                  <Route path="/investigations" element={<InvestigationsPage />} />
                  <Route path="/investigations/:id" element={<InvestigationDetailPage />} />
                  <Route path="/documents" element={<DocumentsPage />} />
                  <Route path="/policies" element={<PolicyCenterPage />} />
                  <Route path="/ai-agents" element={<AiAgentsPage />} />
                  <Route path="/analytics" element={<AnalyticsPage />} />
                  <Route path="/reports" element={<ReportsPage />} />
                  <Route path="/users" element={<ComingSoonPage title="Users & Roles" />} />
                  <Route path="/settings" element={<ComingSoonPage title="Settings" />} />
                </Route>
              </Route>

              <Route path="/404" element={<NotFoundPage />} />
              <Route path="*" element={<Navigate to="/404" replace />} />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
