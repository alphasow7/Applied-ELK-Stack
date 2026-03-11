import { BrowserRouter, Routes, Route, Navigate, Link, useLocation, useNavigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import FarmerDashboard from './pages/FarmerDashboard'
import B2BDashboard from './pages/B2BDashboard'
import MarketPage from './pages/MarketPage'
import USSDSimulator from './pages/USSDSimulator'
import SubscriptionPage from './pages/SubscriptionPage'

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('agritech_token')
  const userData = localStorage.getItem('agritech_user')
  const navigate = useNavigate()
  const location = useLocation()

  if (!token) return <Navigate to="/login" replace />

  const user = userData ? JSON.parse(userData) : null
  const isB2B = user && ['cooperative', 'buyer', 'insurer', 'admin'].includes(user.role)

  const nav = [
    { to: isB2B ? '/dashboard/b2b' : '/dashboard/farmer', label: '🏠 Accueil' },
    { to: '/market', label: '📈 Marchés' },
    { to: '/ussd', label: '📱 USSD/SMS' },
    { to: '/plans', label: '💎 Plans' },
  ]

  const logout = () => {
    localStorage.removeItem('agritech_token')
    localStorage.removeItem('agritech_user')
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed left-0 top-0 h-full w-56 bg-agri-900 text-white flex flex-col">
        <div className="p-4 border-b border-agri-700">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🌾</span>
            <div>
              <p className="font-bold text-lg leading-tight">AgriTech</p>
              <p className="text-agri-400 text-xs">{user?.full_name}</p>
            </div>
          </div>
          <div className="mt-2">
            <span className={`text-xs px-2 py-0.5 rounded-full ${
              isB2B ? 'bg-blue-600 text-blue-100' : 'bg-agri-600 text-agri-100'
            }`}>
              {user?.role}
            </span>
          </div>
        </div>

        <nav className="flex-1 p-3 space-y-1">
          {nav.map((n) => (
            <Link
              key={n.to}
              to={n.to}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                location.pathname === n.to
                  ? 'bg-agri-700 text-white'
                  : 'text-agri-300 hover:bg-agri-800 hover:text-white'
              }`}
            >
              {n.label}
            </Link>
          ))}
        </nav>

        <div className="p-3 border-t border-agri-700">
          <div className="text-xs text-agri-400 mb-2 px-2">
            USSD: <span className="font-mono font-bold text-agri-300">*384*123#</span>
          </div>
          <button onClick={logout} className="w-full text-left text-xs text-agri-400 hover:text-white px-3 py-2 rounded-lg hover:bg-agri-800 transition-colors">
            🚪 Déconnexion
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="ml-56 p-8 min-h-screen">
        <div className="max-w-6xl mx-auto">
          {children}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route
          path="/dashboard/farmer"
          element={<ProtectedLayout><FarmerDashboard /></ProtectedLayout>}
        />
        <Route
          path="/dashboard/b2b"
          element={<ProtectedLayout><B2BDashboard /></ProtectedLayout>}
        />
        <Route
          path="/market"
          element={<ProtectedLayout><MarketPage /></ProtectedLayout>}
        />
        <Route
          path="/ussd"
          element={<ProtectedLayout><USSDSimulator /></ProtectedLayout>}
        />
        <Route
          path="/plans"
          element={<ProtectedLayout><SubscriptionPage /></ProtectedLayout>}
        />
      </Routes>
    </BrowserRouter>
  )
}
