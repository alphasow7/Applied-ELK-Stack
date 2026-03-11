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
        '✅ Accès USSD (*384*123#)',
        '✅ Prévisions météo 7 jours',
        '✅ Prévision de rendement',
        '✅ Alertes SMS',
        '❌ Dashboard web',
        '❌ Prix marchés temps réel',
        '❌ API access',
      ],
    },
    {
      name: 'Coopérative',
      price: '25 000 XOF/mois',
      subtitle: '270 000 XOF/an (10% réduction)',
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
      name: 'Acheteur Industriel',
      price: '75 000 XOF/mois',
      subtitle: '810 000 XOF/an',
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
      price: '150 000 XOF/mois',
      subtitle: '1 620 000 XOF/an',
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
        <h1 className="text-2xl font-bold text-gray-900">Plans & Tarifs</h1>
        <p className="text-gray-500 text-sm">
          Modèle Freemium pour les agriculteurs · SaaS B2B pour les coopératives et acheteurs
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
        <h2 className="font-semibold text-agri-800 mb-3">Programme ONG & Subventions</h2>
        <p className="text-sm text-agri-700">
          Le plan Freemium est proposé gratuitement aux petits agriculteurs grâce à des partenariats
          avec des ONG, des agences de développement agricole et des programmes gouvernementaux de subvention.
          Si votre organisation souhaite financer l'accès pour des communautés agricoles,{' '}
          <span className="font-semibold">contactez-nous à partenariats@agritech.sn</span>.
        </p>
      </div>
    </div>
  )
}
