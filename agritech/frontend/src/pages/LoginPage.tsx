import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../hooks/useApi'

export default function LoginPage() {
  const [phone, setPhone] = useState('+221771234567')
  const [password, setPassword] = useState('farmer123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const DEMO_ACCOUNTS = [
    { label: 'Agriculteur (Moussa)', phone: '+221771234567', pass: 'farmer123' },
    { label: 'Coopérative (Thiès)', phone: '+221701111111', pass: 'coop123' },
    { label: 'Acheteur industriel', phone: '+221702222222', pass: 'buyer123' },
    { label: 'Admin', phone: '+221700000000', pass: 'admin123' },
  ]

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const form = new FormData()
      form.append('username', phone)
      form.append('password', password)
      const res = await api.post('/auth/login', form)
      localStorage.setItem('agritech_token', res.data.access_token)
      localStorage.setItem('agritech_user', JSON.stringify(res.data))
      navigate(res.data.role === 'farmer' ? '/dashboard/farmer' : '/dashboard/b2b')
    } catch {
      setError('Identifiants incorrects. Vérifiez votre numéro et mot de passe.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-agri-800 to-agri-600 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🌾</div>
          <h1 className="text-3xl font-bold text-white">AgriTech</h1>
          <p className="text-agri-200 mt-1">Plateforme de Données Agricoles Prédictives</p>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-6 text-gray-800">Connexion</h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg mb-4 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Numéro de téléphone
              </label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-agri-500"
                placeholder="+221771234567"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mot de passe
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-agri-500"
                required
              />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>

          <div className="mt-6 border-t pt-4">
            <p className="text-xs text-gray-500 mb-2 font-medium">Comptes démo :</p>
            <div className="grid grid-cols-2 gap-2">
              {DEMO_ACCOUNTS.map((a) => (
                <button
                  key={a.phone}
                  onClick={() => { setPhone(a.phone); setPassword(a.pass) }}
                  className="text-xs bg-agri-50 hover:bg-agri-100 text-agri-700 px-2 py-1.5 rounded border border-agri-200 text-left truncate"
                >
                  {a.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-6 card text-center">
          <p className="text-sm text-gray-600 font-medium mb-2">Agriculteurs sans smartphone</p>
          <div className="bg-agri-50 rounded-lg p-3 font-mono text-lg text-agri-700 font-bold tracking-widest">
            *384*123#
          </div>
          <p className="text-xs text-gray-400 mt-1">USSD disponible sur tout téléphone</p>
        </div>
      </div>
    </div>
  )
}
