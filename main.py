import os
import json
import time
import requests
from collections import defaultdict

# ⚙️ CONFIG
SYSTEM_NAME = "rens"
MIN_ECART_PCT = 10
MIN_VOLUME_PAR_JOUR = 3
FORCE_REFRESH = False

ESI_BASE = "https://esi.evetech.net/latest"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "EVE-Market-Scanner/Auto"
}

TRADE_HUBS = {
    "jita": 30000142,
    "amarr": 30002187,
    "dodixie": 30002659,
    "rens": 30002510,
    "hek": 30002053
}
HARDCODED_SYSTEMS = {
    30000142: 10000002,
    30002187: 10000043,
    30002659: 10000032,
    30002510: 10000030,
    30002053: 10000042
}


# 🔁 API Retry
def esi_get(endpoint, params=None):
    url = f"{ESI_BASE}{endpoint}"
    while True:
        try:
            resp = requests.get(url, params=params, headers=HEADERS)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Erreur API : {e} → retry dans 2s")
            time.sleep(2)


# 🔧 Utilitaires
def get_system_and_region(system_name):
    system_id = TRADE_HUBS.get(system_name.lower())
    region_id = HARDCODED_SYSTEMS.get(system_id)
    if not system_id or not region_id:
        print(f"❌ Système '{system_name}' inconnu.")
        return None, None
    return system_id, region_id


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


# 📦 Récupération des données
def fetch_orders(region_id):
    cache_path = f"orders_{region_id}.json"
    if not FORCE_REFRESH and os.path.exists(cache_path):
        print("♻️ Chargement des ordres depuis le cache...")
        return load_json(cache_path)

    print("⏬ Téléchargement des ordres de marché...")
    all_orders = []
    page = 1
    while True:
        page_orders = esi_get(f"/markets/{region_id}/orders/", {"page": page})
        if not page_orders:
            break
        all_orders.extend(page_orders)
        print(f"Page {page}: {len(page_orders)} ordres", end='\r')
        if len(page_orders) < 1000:
            break
        page += 1
        time.sleep(0.2)

    save_json(cache_path, all_orders)
    print(f"\n✅ {len(all_orders):,} ordres sauvegardés")
    return all_orders


def fetch_history(region_id, type_ids):
    cache_path = f"history_{region_id}.json"
    if os.path.exists(cache_path) and not FORCE_REFRESH:
        return load_json(cache_path)

    print("⏬ Téléchargement de l'historique de volume pour chaque item...")
    history = {}
    for idx, type_id in enumerate(type_ids, 1):
        print(f"Volume {idx}/{len(type_ids)} - ID {type_id}", end='\r')
        data = esi_get(f"/markets/{region_id}/history/", {"type_id": type_id})
        if data:
            history[str(type_id)] = data
        time.sleep(0.2)

    save_json(cache_path, history)
    return history


def fetch_names(type_ids):
    path = "types.json"
    names = load_json(path) or {}
    needed = [tid for tid in type_ids if str(tid) not in names]

    print(f"⏬ Récupération des noms pour {len(needed)} items manquants...")
    for idx, type_id in enumerate(needed, 1):
        print(f"Nom {idx}/{len(needed)} - ID {type_id}", end='\r')
        data = esi_get(f"/universe/types/{type_id}/")
        if data:
            names[str(type_id)] = data.get("name", f"Type {type_id}")
        time.sleep(0.2)

    save_json(path, names)
    return names


# 🔍 Analyse
def group_orders(orders, system_id):
    items = defaultdict(list)
    for order in orders:
        if order["system_id"] == system_id:
            items[order["type_id"]].append(order)
    return items


def get_daily_volume(type_id, history):
    entries = history.get(str(type_id), [])
    last_7 = entries[-7:]
    vols = [e["volume"] for e in last_7]
    return sum(vols) / len(vols) if vols else 0


def analyze(items_by_type, types_data, history_data):
    results = []
    for idx, (type_id, orders) in enumerate(items_by_type.items(), 1):
        print(f"Analyse {idx}/{len(items_by_type)}", end='\r')

        sell = [o for o in orders if not o["is_buy_order"]]
        buy = [o for o in orders if o["is_buy_order"]]
        if not sell or not buy:
            continue

        best_sell = min(sell, key=lambda o: o["price"])["price"]
        best_buy = max(buy, key=lambda o: o["price"])["price"]
        if best_buy == 0:
            continue

        ecart_pct = ((best_sell - best_buy) / best_buy) * 100
        if ecart_pct < MIN_ECART_PCT:
            continue

        vol = get_daily_volume(type_id, history_data)
        if vol < MIN_VOLUME_PAR_JOUR:
            continue

        results.append({
            "name": types_data.get(str(type_id), f"Type {type_id}"),
            "buy": best_buy,
            "sell": best_sell,
            "ecart_pct": round(ecart_pct, 2),
            "vol_jour": round(vol, 1)
        })

    print("✅ Analyse complète")
    return sorted(results, key=lambda x: x["ecart_pct"], reverse=True)


# ▶️ MAIN
if __name__ == "__main__":
    system_id, region_id = get_system_and_region(SYSTEM_NAME)
    if not region_id:
        exit(1)

    orders = fetch_orders(region_id)
    type_ids = {o["type_id"] for o in orders if o["system_id"] == system_id}
    history = fetch_history(region_id, type_ids)
    types = fetch_names(type_ids)

    items = group_orders(orders, system_id)
    results = analyze(items, types, history)

    print("\n📈 TOP OPPORTUNITÉS:")
    for r in results[:15]:
        print(f"- {r['name']}: Achat {r['buy']} → Vente {r['sell']} "
              f"(+{r['ecart_pct']}%) | Qté/jour: {r['vol_jour']}")
