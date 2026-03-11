"""
USSD/SMS Handler compatible avec Orange Guinea / MTN Guinea (Africa's Talking).
USSD flow: *384*1# → menu → submenu → réponse

Opérateurs Guinée : Orange Guinea (+224 620-629), MTN Guinea (+224 660-663)
Code USSD national : *384*1#  (à valider avec l'opérateur local)

Menu structure (FR — langues locales: Pular, Malinké, Susu à venir):
1. Prix du marché
2. Météo & Sol
3. Mon rendement prévu
4. Conseils saison
5. Mon compte
"""
from fastapi import APIRouter, Form, Request
from typing import Optional
from app.services.market_service import get_current_prices, get_market_trends, COMMODITIES
from app.services.weather_service import fetch_weather, get_soil_health_score, compute_yield_prediction, _simulate_weather
from app.core.logging import logger

router = APIRouter(tags=["USSD/SMS"])

# Cultures prioritaires en Guinée (USSD = max 6 options lisibles sur écran basique)
CROP_LIST = ["riz", "manioc", "fonio", "maïs", "arachide", "café"]


def _fmt_price(commodity: str, region: str = None) -> str:
    prices = get_current_prices(commodity, region)
    if not prices:
        return f"Aucun prix pour {commodity}."
    avg = sum(p["price_per_kg"] for p in prices) / len(prices)
    mn = min(p["price_per_kg"] for p in prices)
    mx = max(p["price_per_kg"] for p in prices)
    label = commodity.replace("_", " ").upper()
    return (
        f"{label}\n"
        f"Moy: {int(avg):,} GNF/kg\n"
        f"Min: {int(mn):,} | Max: {int(mx):,}\n"
        f"Marchés: {len(prices)}"
    )


def _fmt_weather(region: str = "Conakry") -> str:
    # 5 villes représentatives des 4 régions naturelles de Guinée
    REGIONS = {
        "Conakry":    (9.55,  -13.68),   # Basse-Guinée
        "Kindia":     (10.05, -12.87),   # Basse-Guinée
        "Labé":       (11.32, -12.29),   # Moyenne-Guinée
        "Kankan":     (10.39,  -9.31),   # Haute-Guinée
        "N'Zérékoré": (7.75,  -8.82),   # Guinée Forestière
    }
    coords = REGIONS.get(region, (9.55, -13.68))
    data = _simulate_weather(*coords, 3)
    d = data["daily"]
    lines = [f"MÉTÉO {region}"]
    for i in range(min(3, len(d["time"]))):
        lines.append(
            f"{d['time'][i]}: {d['temperature_2m_max'][i]}°C "
            f"Pluie:{d['precipitation_sum'][i]}mm"
        )
    return "\n".join(lines)


def _fmt_yield(crop: str = "riz", area: float = 1.0) -> str:
    data = _simulate_weather(9.55, -13.68, 7)  # Conakry par défaut
    soil = get_soil_health_score(9.55, -13.68)
    pred = compute_yield_prediction(crop, area, data, soil["health_score"])
    risk_emoji = {"low": "✓", "medium": "~", "high": "!"}.get(pred["risk_level"], "~")
    return (
        f"RENDEMENT PRÉVU\n"
        f"Culture: {crop}\n"
        f"Surface: {area}ha\n"
        f"Prévu: {int(pred['predicted_yield_kg'])}kg\n"
        f"Risque: {risk_emoji}{pred['risk_level']}\n"
        f"Conseil: {pred['recommendation'][:60]}..."
    )


def _process_ussd(session_id: str, phone: str, text: str) -> str:
    steps = [s for s in text.split("*") if s] if text else []

    # Root menu
    if not steps:
        return (
            "CON AgriTech Guinée\n"
            "1. Prix marchés\n"
            "2. Météo & Sol\n"
            "3. Rendement prévu\n"
            "4. Conseils saison\n"
            "5. Mon compte"
        )

    level1 = steps[0]

    # --- PRIX MARCHÉS ---
    if level1 == "1":
        if len(steps) == 1:
            menu = "CON PRIX DU MARCHÉ\n"
            for i, c in enumerate(CROP_LIST, 1):
                menu += f"{i}. {c.capitalize()}\n"
            menu += "7. Retour"
            return menu
        if len(steps) == 2:
            idx = int(steps[1]) - 1
            if 0 <= idx < len(CROP_LIST):
                result = _fmt_price(CROP_LIST[idx])
                return f"END {result}"
            return "END Choix invalide."

    # --- MÉTÉO & SOL ---
    elif level1 == "2":
        if len(steps) == 1:
            return (
                "CON MÉTÉO & SOL\n"
                "1. Conakry\n"
                "2. Kindia\n"
                "3. Labé\n"
                "4. Kankan\n"
                "5. N'Zérékoré"
            )
        if len(steps) == 2:
            regions = ["Conakry", "Kindia", "Labé", "Kankan", "N'Zérékoré"]
            idx = int(steps[1]) - 1
            if 0 <= idx < len(regions):
                result = _fmt_weather(regions[idx])
                return f"END {result}"
            return "END Région invalide."

    # --- RENDEMENT ---
    elif level1 == "3":
        if len(steps) == 1:
            menu = "CON RENDEMENT PRÉVU\nChoisir culture:\n"
            for i, c in enumerate(CROP_LIST, 1):
                menu += f"{i}. {c.capitalize()}\n"
            return menu
        if len(steps) == 2:
            return "CON Surface (en ha):\n1. 0.5ha\n2. 1ha\n3. 2ha\n4. 5ha"
        if len(steps) == 3:
            idx = int(steps[1]) - 1
            areas = [0.5, 1.0, 2.0, 5.0]
            area_idx = int(steps[2]) - 1
            if 0 <= idx < len(CROP_LIST) and 0 <= area_idx < len(areas):
                result = _fmt_yield(CROP_LIST[idx], areas[area_idx])
                return f"END {result}"
            return "END Entrée invalide."

    # --- CONSEILS SAISON ---
    elif level1 == "4":
        return (
            "END CONSEILS SAISON\n"
            "• Saison des pluies (mai-oct): préparez les bas-fonds pour le riz\n"
            "• Réduisez les pertes post-récolte: séchez bien avant stockage\n"
            "• Utilisez des sacs hermétiques (PICS) contre les insectes\n"
            "• Café/fonio: vendez à Conakry pour meilleur prix\n"
            "• Protégez les tubercules (manioc) de l'humidité excessive"
        )

    # --- MON COMPTE ---
    elif level1 == "5":
        return (
            "END MON COMPTE\n"
            f"Tél: {phone}\n"
            "Plan: Freemium (gratuit)\n"
            "Pour upgrader:\n"
            "agritech.gn/upgrade\n"
            "ou SMS: UPGRADE au 3434\n"
            "Orange/MTN Guinea"
        )

    return "END Choix invalide. Rappeler *384*1#"


@router.post("/ussd")
async def ussd_handler(
    request: Request,
    sessionId: str = Form(...),
    phoneNumber: str = Form(...),
    networkCode: str = Form(default="62101"),
    serviceCode: str = Form(default="*384*1#"),
    text: str = Form(default=""),
):
    logger.info(f"USSD session={sessionId} phone={phoneNumber} text={text}")
    response = _process_ussd(sessionId, phoneNumber, text)
    return response  # Africa's Talking expects plain text


@router.post("/sms/incoming")
async def sms_handler(
    request: Request,
    from_: str = Form(default="", alias="from"),
    to: str = Form(default=""),
    text: str = Form(default=""),
    date: str = Form(default=""),
):
    """Handle incoming SMS commands."""
    cmd = text.strip().upper()
    logger.info(f"SMS from={from_} cmd={cmd}")

    responses = {
        "PRIX RIZ":     _fmt_price("riz"),
        "PRIX FONIO":   _fmt_price("fonio"),
        "PRIX MANIOC":  _fmt_price("manioc"),
        "PRIX CAFE":    _fmt_price("café"),
        "PRIX MAIS":    _fmt_price("maïs"),
        "METEO":        _fmt_weather("Conakry"),
        "AIDE": (
            "AgriTech Guinée - SMS:\n"
            "PRIX [culture] - Prix du marché\n"
            "Ex: PRIX RIZ, PRIX FONIO\n"
            "METEO - Météo du jour\n"
            "AIDE - Ce menu\n"
            "Orange/MTN +224"
        ),
    }

    # Dynamic PRIX command
    if cmd.startswith("PRIX "):
        crop = cmd[5:].lower().replace(" ", "_")
        if crop in COMMODITIES:
            sms_text = _fmt_price(crop)
        else:
            readable = [c.replace("_", " ") for c in COMMODITIES]
            sms_text = f"Culture inconnue. Essayer: {', '.join(readable)}"
    else:
        sms_text = responses.get(cmd, "Tapez AIDE pour les commandes.")

    return {"message": sms_text, "recipient": from_}


@router.get("/ussd/demo")
async def ussd_demo():
    """Demo endpoint showing USSD flow without a real gateway."""
    flows = {
        "root": _process_ussd("demo", "+224620000000", ""),
        "market_menu": _process_ussd("demo", "+224620000000", "1"),
        "mil_price": _process_ussd("demo", "+224620000000", "1*1"),
        "weather_menu": _process_ussd("demo", "+224620000000", "2"),
        "weather_thies": _process_ussd("demo", "+224620000000", "2*2"),
        "yield_crop": _process_ussd("demo", "+224620000000", "3"),
        "yield_surface": _process_ussd("demo", "+224620000000", "3*1"),
        "yield_result": _process_ussd("demo", "+224620000000", "3*1*2"),
        "tips": _process_ussd("demo", "+224620000000", "4"),
    }
    return {"ussd_flows": flows}
