import { useState } from 'react'
import { api } from '../hooks/useApi'

interface UssdFlow {
  ussd_flows: Record<string, string>
}

export default function USSDSimulator() {
  const [sessionText, setSessionText] = useState('')
  const [response, setResponse] = useState('')
  const [phone, setPhone] = useState('+221771234567')
  const [history, setHistory] = useState<{ input: string; output: string }[]>([])
  const [preloaded, setPreloaded] = useState<UssdFlow | null>(null)

  const loadDemo = async () => {
    const res = await api.get('/ussd/demo')
    setPreloaded(res.data)
  }

  const sendUSSD = async () => {
    const formData = new FormData()
    formData.append('sessionId', `session_${Date.now()}`)
    formData.append('phoneNumber', phone)
    formData.append('networkCode', '62101')
    formData.append('serviceCode', '*384*123#')
    formData.append('text', sessionText)

    const res = await api.post('/ussd', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const out = typeof res.data === 'string' ? res.data : JSON.stringify(res.data)
    setResponse(out)
    setHistory((h) => [...h, { input: sessionText || '(root)', output: out }])
  }

  const isEnd = response.startsWith('END ')
  const isCon = response.startsWith('CON ')
  const displayText = response.replace(/^(CON|END) /, '')

  const QUICK_NAVIGATIONS = [
    { label: 'Menu principal', text: '' },
    { label: '1. Prix marchés', text: '1' },
    { label: '  1.1 Prix mil', text: '1*1' },
    { label: '  1.3 Prix arachide', text: '1*3' },
    { label: '2. Météo', text: '2' },
    { label: '  2.2 Météo Thiès', text: '2*2' },
    { label: '3. Rendement', text: '3' },
    { label: '  3.1 Mil, 1ha', text: '3*1*2' },
    { label: '4. Conseils', text: '4' },
    { label: '5. Mon compte', text: '5' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Simulateur USSD/SMS</h1>
        <p className="text-gray-500 text-sm">
          Testez l'interface USSD accessible via <span className="font-mono font-bold">*384*123#</span> sur tout téléphone
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Phone simulator */}
        <div className="card">
          <h2 className="font-semibold mb-4">Téléphone simulé</h2>

          <div className="bg-gray-900 rounded-2xl p-4 font-mono text-sm text-green-400 min-h-48 mb-4 whitespace-pre-wrap">
            {response ? (
              <>
                {displayText}
                {isCon && <span className="animate-pulse block mt-2">█</span>}
                {isEnd && <span className="block mt-2 text-gray-500">[Session terminée]</span>}
              </>
            ) : (
              <span className="text-gray-600">Appuyez sur "Envoyer" pour démarrer...</span>
            )}
          </div>

          <div className="space-y-3">
            <div className="flex gap-2">
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="Numéro de téléphone"
                className="flex-1 border rounded-lg px-3 py-2 text-sm"
              />
            </div>
            <div className="flex gap-2">
              <input
                value={sessionText}
                onChange={(e) => setSessionText(e.target.value)}
                placeholder='Entrée USSD (ex: "1*2")'
                className="flex-1 border rounded-lg px-3 py-2 text-sm font-mono"
              />
              <button onClick={sendUSSD} className="btn-primary">Envoyer</button>
            </div>
            <button
              onClick={() => { setSessionText(''); setResponse(''); setHistory([]) }}
              className="btn-secondary w-full text-sm"
            >
              Réinitialiser la session
            </button>
          </div>
        </div>

        {/* Navigation shortcuts */}
        <div className="card">
          <h2 className="font-semibold mb-4">Navigation rapide</h2>
          <div className="space-y-2">
            {QUICK_NAVIGATIONS.map((nav) => (
              <button
                key={nav.text}
                onClick={() => { setSessionText(nav.text); }}
                className="w-full text-left px-3 py-2 text-sm hover:bg-agri-50 rounded-lg border border-transparent hover:border-agri-200 flex items-center justify-between"
              >
                <span>{nav.label}</span>
                <code className="text-xs bg-gray-100 px-2 py-0.5 rounded text-gray-600">
                  {nav.text || 'ROOT'}
                </code>
              </button>
            ))}
          </div>

          <button onClick={loadDemo} className="btn-secondary mt-4 w-full text-sm">
            Charger toutes les démos
          </button>

          {preloaded && (
            <div className="mt-4 space-y-2 max-h-64 overflow-y-auto">
              {Object.entries(preloaded.ussd_flows).map(([key, val]) => (
                <div key={key} className="bg-gray-50 rounded p-2 text-xs">
                  <p className="font-semibold text-gray-700 mb-1">{key}</p>
                  <pre className="text-gray-600 whitespace-pre-wrap">{val}</pre>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Session history */}
      {history.length > 0 && (
        <div className="card">
          <h2 className="font-semibold mb-4">Historique de session</h2>
          <div className="space-y-3">
            {history.map((h, i) => (
              <div key={i} className="flex gap-4 text-sm">
                <div className="w-1/3 bg-blue-50 rounded p-2">
                  <p className="text-xs text-gray-400 mb-1">Entrée</p>
                  <code>{h.input || '(root)'}</code>
                </div>
                <div className="flex-1 bg-gray-50 rounded p-2 font-mono text-xs whitespace-pre-wrap text-green-700">
                  {h.output}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SMS info */}
      <div className="card bg-blue-50 border-blue-200">
        <h2 className="font-semibold text-blue-800 mb-3">Commandes SMS disponibles</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
          {[
            { cmd: 'PRIX MIL', desc: 'Prix du mil sur les marchés' },
            { cmd: 'PRIX ARACHIDE', desc: 'Prix de l\'arachide' },
            { cmd: 'PRIX RIZ', desc: 'Prix du riz' },
            { cmd: 'METEO', desc: 'Météo du jour' },
            { cmd: 'AIDE', desc: 'Liste des commandes' },
          ].map((s) => (
            <div key={s.cmd} className="bg-white rounded-lg p-3 border border-blue-100">
              <code className="font-bold text-blue-700">{s.cmd}</code>
              <p className="text-xs text-gray-500 mt-1">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
