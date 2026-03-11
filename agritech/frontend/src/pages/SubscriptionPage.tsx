export default function SubscriptionPage() {
  const PLANS = [
    {
      name: 'Freemium Agriculteur',
      price: 'Gratuit',
      subtitle: 'Financé par ONG / subventions',
      color: 'border-agri-200 bg-agri-50',
      badge: 'bg-agri-100 text-agri-700',
      badgeText: 'GRATUIT',
      features: [
        '✅ Accès USSD (*384*1#) — Orange/MTN Guinée',
        '✅ Prévisions météo 7 jours',
        '✅ Prévision de rendement',
        '✅ Alertes SMS',
        '❌ Dashboard web',
        '❌ Prix marchés temps réel',
        '❌ API access',
      ],
    },
    {
      name: 'Coopérative / Groupement',
      price: '200 000 GNF/mois',
      subtitle: '2 160 000 GNF/an (10% réduction) · ~21 EUR',
      color: 'border-blue-300 bg-blue-50',
      badge: 'bg-blue-100 text-blue-700',
      badgeText: 'B2B',
      popular: true,
      features: [
        '✅ Tout ce qui est dans Freemium',
        '✅ Dashboard web complet',
        '✅ Prix marchés temps réel',
        '✅ Gestion jusqu\'à 200 champs',
        '✅ Analytics et tendances',
        '✅ 10 comptes utilisateurs',
        '❌ API access',
        '❌ Module assurance',
      ],
    },
    {
      name: 'Acheteur / Exportateur',
      price: '650 000 GNF/mois',
      subtitle: '7 020 000 GNF/an · ~69 EUR',
      color: 'border-purple-300 bg-purple-50',
      badge: 'bg-purple-100 text-purple-700',
      badgeText: 'ENTREPRISE',
      features: [
        '✅ Tout ce qui est dans Coopérative',
        '✅ Accès API complet',
        '✅ Prévision d\'offre nationale',
        '✅ Opportunités commerciales',
        '✅ Jusqu\'à 5000 champs',
        '✅ 50 comptes utilisateurs',
        '✅ Support prioritaire',
      ],
    },
    {
      name: 'Assureur Agricole',
      price: '1 300 000 GNF/mois',
      subtitle: '14 040 000 GNF/an · ~138 EUR',
      color: 'border-amber-300 bg-amber-50',
      badge: 'bg-amber-100 text-amber-700',
      badgeText: 'ASSUREUR',
      features: [
        '✅ Tout ce qui est dans Entreprise',
        '✅ Module assurance paramétrique',
        '✅ Scoring de risque par champ',
        '✅ Données satellites complètes',
        '✅ Indices NDVI en temps réel',
        '✅ Champs illimités',
        '✅ 100 comptes utilisateurs',
        '✅ SLA garanti 99.9%',
      ],
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Plans & Tarifs — Guinée</h1>
        <p className="text-gray-500 text-sm">
          Freemium pour les agriculteurs (financé ONG) · SaaS B2B pour coopératives, exportateurs et assureurs · Prix en GNF (Franc Guinéen)
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {PLANS.map((plan) => (
          <div
            key={plan.name}
            className={`relative card border-2 ${plan.color} ${plan.popular ? 'shadow-lg scale-105' : ''}`}
          >
            {plan.popular && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                  LE PLUS POPULAIRE
                </span>
              </div>
            )}
            <div className="mb-4">
              <span className={`badge ${plan.badge} text-xs`}>{plan.badgeText}</span>
              <h2 className="text-lg font-bold mt-2">{plan.name}</h2>
              <p className="text-2xl font-bold text-gray-900 mt-2">{plan.price}</p>
              <p className="text-xs text-gray-400 mt-1">{plan.subtitle}</p>
            </div>
            <ul className="space-y-2 text-sm text-gray-700">
              {plan.features.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
            <button className="btn-primary w-full mt-6 text-sm">
              {plan.price === 'Gratuit' ? 'Commencer gratuitement' : 'Contacter les ventes'}
            </button>
          </div>
        ))}
      </div>

      <div className="card bg-agri-50 border-agri-200">
        <h2 className="font-semibold text-agri-800 mb-3">Programme ONG & Partenaires en Guinée</h2>
        <p className="text-sm text-agri-700">
          Le plan Freemium est proposé gratuitement aux petits agriculteurs grâce à des partenariats
          avec des ONG actives en Guinée : <strong>USAID Feed the Future, FAO Guinée, GIZ, FIDA, Banque Mondiale</strong>,
          et le Ministère de l'Agriculture de Guinée (ANPROCA). Les coopératives rurales peuvent bénéficier
          de subventions via le programme PNDA (Plan National de Développement Agricole).{' '}
          <span className="font-semibold">Contactez-nous : partenariats@agritech.gn</span>
        </p>
      </div>
    </div>
  )
}
