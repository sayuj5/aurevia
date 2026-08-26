import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './lib/auth'
import { AppShell } from './components/AppShell'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Landing } from './pages/Landing'
import { Assessment } from './pages/Assessment'
import { PatientLogin } from './pages/PatientLogin'
import { PatientRegister } from './pages/PatientRegister'
import { Dashboard } from './pages/Dashboard'
import { CaseManagement } from './pages/CaseManagement'
import { ReportView } from './pages/ReportView'
import { Analytics } from './pages/Analytics'
import { MapView } from './pages/MapView'
import { Notifications } from './pages/Notifications'
import { Admin } from './pages/Admin'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/assessment" element={<Assessment />} />
          <Route path="/login" element={<PatientLogin />} />
          <Route path="/register" element={<PatientRegister />} />

          <Route element={<ProtectedRoute />}>
            <Route element={<AppShell />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/cases" element={<CaseManagement />} />
              <Route path="/cases/:id/report" element={<ReportView />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/map" element={<MapView />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="/admin" element={<Admin />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
