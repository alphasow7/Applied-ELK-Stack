# 🌾 AgriTech — Plateforme de Données Prédictives pour l'Agriculture

> Système d'information agricole dual-canal : **USSD/SMS** pour les agriculteurs sans smartphone + **Dashboard Web** pour les coopératives et acheteurs industriels.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AGRITECH PLATFORM                          │
│                                                                 │
│  ┌──────────────┐    ┌─────────────────────────────────────┐   │
│  │ Agriculteurs │    │          B2B (SaaS)                 │   │
│  │ sans smart-  │    │  Coopératives · Acheteurs · Assureurs│  │
│  │    phone     │    └──────────────┬──────────────────────┘   │
│  └──────┬───────┘                   │                          │
│         │ USSD *384*123#            │ Web Dashboard            │
│         │ SMS texte                 │ REST API                 │
│         ▼                           ▼                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend (Python)                    │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │  │
│  │  │  USSD /  │ │  Market  │ │ Weather  │ │ Analytics │  │  │
│  │  │  SMS API │ │   API    │ │  & Soil  │ │  B2B API  │  │  │
│  │  └──────────┘ └──────────┘ └────┬─────┘ └───────────┘  │  │
│  └───────────────────────────────┬─┘──────────────────────┘   │
│                                  │                              │
│  ┌──────────────┐  ┌─────────────┴──────┐  ┌────────────────┐ │
│  │ Open-Meteo   │  │   SQLite / Postgres │  │ Africa's Talk. │ │
│  │ (Satellite   │  │   (ORM AsyncSQL)    │  │ (USSD/SMS GW)  │ │
│  │  Weather)    │  └────────────────────┘  └────────────────┘ │
│  └──────────────┘                                              │
│                                                                 │
│  ┌─────────────────── ELK Stack ──────────────────────────┐   │
│  │ Filebeat → Logstash → Elasticsearch → Kibana           │   │
│  │ (Logs API · Canaux USSD/SMS/Web · Monitoring)          │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Fonctionnalités

### Pour les agriculteurs (Freemium — USSD/SMS)
- 📱 **Interface USSD** (`*384*123#`) — accessible sur tout téléphone basique
- 💬 **Commandes SMS** — PRIX MIL, METEO, AIDE...
- 🌦️ **Météo locale précise** — 7 jours, données satellites via Open-Meteo
- 📊 **Prévision de rendement** — modèle prédictif par culture et surface
- ⚠️ **Alertes SMS** — risques météo, ravageurs, opportunités de vente

### Pour les coopératives (25 000 XOF/mois)
- 🗺️ **Dashboard web** — carte interactive des exploitations
- 📈 **Prix marchés temps réel** — 8 marchés, 8 cultures
- 📉 **Historique et tendances** — 30/90/365 jours
- 👥 **Gestion groupée** — jusqu'à 200 champs, 10 utilisateurs

### Pour les acheteurs industriels (75 000 XOF/mois)
- 🔗 **API REST complète** — intégration ERP/WMS
- 🏪 **Opportunités commerciales** — spread inter-marchés automatique
- 📦 **Prévision d'offre** — volume disponible par culture/région

### Pour les assureurs agricoles (150 000 XOF/mois)
- 🛡️ **Scoring de risque paramétrique** — sécheresse, inondation, ravageurs
- 💰 **Calcul de prime automatique** — taux suggéré par champ
- 🌍 **Données NDVI** — santé de la végétation via satellite

---

## Démarrage rapide

### Avec Docker Compose (recommandé)
```bash
cd agritech
cp .env.example .env
docker-compose up -d
```

Services disponibles :
| Service | URL |
|---------|-----|
| Frontend React | http://localhost:3000 |
| API Backend | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/api/docs |
| Kibana | http://localhost:5601 |
| Elasticsearch | http://localhost:9200 |

### Développement local

**Backend :**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend :**
```bash
cd frontend
npm install
npm run dev
```

---

## Comptes de démo

| Rôle | Téléphone | Mot de passe |
|------|-----------|--------------|
| Agriculteur (Moussa Diallo) | +221771234567 | farmer123 |
| Coopérative (Thiès Nord) | +221701111111 | coop123 |
| Acheteur (Senagri Industries) | +221702222222 | buyer123 |
| Admin | +221700000000 | admin123 |

---

## Interface USSD

Simuler via `GET /api/ussd/demo` ou via le simulateur intégré dans le dashboard.

```
*384*123#
├── 1. Prix marchés
│   ├── 1. Mil
│   ├── 2. Sorgho
│   ├── 3. Arachide
│   └── ...
├── 2. Météo & Sol
│   ├── 1. Dakar
│   ├── 2. Thiès
│   └── ...
├── 3. Rendement prévu
│   ├── (choisir culture)
│   └── (choisir surface)
├── 4. Conseils agricoles
└── 5. Mon compte
```

**Commandes SMS :**
```
PRIX MIL        → Prix du mil sur tous les marchés
PRIX ARACHIDE   → Prix de l'arachide
METEO           → Météo du jour
AIDE            → Liste des commandes
```

---

## API Reference

### Endpoints principaux

```
POST /api/auth/register          Inscription
POST /api/auth/login             Connexion (retourne JWT)
GET  /api/auth/me                Profil utilisateur

GET  /api/farmers/dashboard      Tableau de bord agriculteur
GET  /api/farmers/farms          Mes champs
POST /api/farmers/farms          Créer un champ
POST /api/farmers/farms/{id}/predict  Lancer prédiction de rendement

GET  /api/market/prices          Prix des marchés
GET  /api/market/prices/history/{commodity}  Historique
GET  /api/market/trends/{commodity}          Tendances
GET  /api/market/opportunities   Opportunités de trading

GET  /api/weather/forecast?lat=&lon=  Météo par coordonnées
GET  /api/weather/region/{region}     Météo par région
GET  /api/weather/soil?lat=&lon=      Santé du sol

POST /api/ussd                   Handler USSD (Africa's Talking)
POST /api/sms/incoming           Handler SMS entrant
GET  /api/ussd/demo              Démo des flux USSD

GET  /api/analytics/overview         Vue d'ensemble plateforme (B2B)
GET  /api/analytics/supply-forecast  Prévision d'offre (B2B)
GET  /api/analytics/risk-heatmap     Carte des risques (B2B)
GET  /api/analytics/insurance-scoring Scoring assurance (Assureurs)
```

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Backend API | FastAPI (Python 3.12) |
| ORM | SQLAlchemy 2 (async) |
| Base de données | SQLite (dev) / PostgreSQL (prod) |
| Frontend | React 18 + TypeScript + Vite |
| Styling | Tailwind CSS |
| Cartes | Leaflet / React-Leaflet |
| Graphiques | Recharts |
| Auth | JWT (python-jose) |
| USSD/SMS | Africa's Talking compatible |
| Météo | Open-Meteo API (gratuit, données satellites) |
| Logs | ELK Stack (Elasticsearch, Logstash, Kibana) |
| Monitoring | Filebeat (Docker logs) |
| Conteneurs | Docker Compose |

---

## Business Model

```
┌─────────────────┬────────────────────────────────────────┐
│ Segment         │ Modèle                                 │
├─────────────────┼────────────────────────────────────────┤
│ Petits          │ GRATUIT — financé par ONG /            │
│ agriculteurs    │ subventions gouvernementales           │
├─────────────────┼────────────────────────────────────────┤
│ Coopératives    │ 25 000 XOF/mois (270 000/an)          │
├─────────────────┼────────────────────────────────────────┤
│ Acheteurs       │ 75 000 XOF/mois (810 000/an)          │
│ industriels     │                                        │
├─────────────────┼────────────────────────────────────────┤
│ Assureurs       │ 150 000 XOF/mois (1 620 000/an)       │
│ agricoles       │                                        │
└─────────────────┴────────────────────────────────────────┘
```

---

## ELK Stack — Monitoring

Après démarrage, importer les dashboards Kibana :
```bash
curl -X POST http://localhost:5601/api/saved_objects/_import \
  -H "kbn-xsrf: true" \
  -F file=@elk/kibana-dashboards.ndjson
```

Dashboards inclus :
- **API Requests over Time** — volume de requêtes par heure
- **USSD vs Web vs SMS** — distribution des canaux d'accès
- **API Error Rate** — taux d'erreurs 4xx/5xx
- **Slow Requests** — requêtes > 500ms
