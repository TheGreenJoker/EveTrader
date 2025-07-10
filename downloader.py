import requests
import time


_item_name_cache = {}
def get_item_name(type_id):
    """
    Récupère le nom d’un item EVE Online via l’ESI.
    Utilise un cache simple pour éviter les appels répétés.
    """
    if type_id in _item_name_cache:
        return _item_name_cache[type_id]
    
    url = f"https://esi.evetech.net/latest/universe/types/{type_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        name = data.get("name", f"Unknown-{type_id}")
        _item_name_cache[type_id] = name
        return name
    else:
        return f"Unknown-{type_id}"


def get_all_type_ids(region_id):
    """Récupère tous les type_id disponibles pour le marché d'une région."""
    url = f"https://esi.evetech.net/latest/markets/{region_id}/types/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_average_volume_per_day(region_id, type_id, days=7):
    """Retourne la moyenne du volume vendu par jour pour un type_id sur les derniers jours."""
    url = f"https://esi.evetech.net/latest/markets/{region_id}/history/?type_id={type_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return 0
    history = response.json()
    if len(history) == 0:
        return 0
    recent_days = history[-days:]
    avg_volume = sum(day['volume'] for day in recent_days) / len(recent_days)
    return avg_volume


def get_market_orders(region_id, order_type):
    assert order_type in ['buy', 'sell']
    orders = []
    page = 1
    while True:
        url = f"https://esi.evetech.net/latest/markets/{region_id}/orders/?order_type={order_type}&page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        orders.extend(data)
        print(f"  -> {order_type} orders page {page}", end='\r')
        if 'X-Pages' in response.headers and page >= int(response.headers['X-Pages']):
            break
        page += 1
        time.sleep(0.1)
    print(f"  ✓  {order_type} orders récupérés")
    return orders


def filter_orders_by_item_and_station(orders, type_id, station_id):
    """Filtre les ordres pour un item donné et une station spécifique."""
    return [o for o in orders if o['type_id'] == type_id and o['location_id'] == station_id]


def summarize_item_market_data(type_id, region_id, station_id, avg_volume, sell_orders, buy_orders):
    """Produit un résumé des données de marché pour un item donné."""
    sell_filtered = filter_orders_by_item_and_station(sell_orders, type_id, station_id)
    buy_filtered = filter_orders_by_item_and_station(buy_orders, type_id, station_id)

    min_sell = min([o['price'] for o in sell_filtered], default=None)
    max_buy = max([o['price'] for o in buy_filtered], default=None)
    total_sell_volume = sum([o['volume_remain'] for o in sell_filtered])
    total_buy_volume = sum([o['volume_remain'] for o in buy_filtered])

    return {
        'type_id': type_id,
        'avg_volume_per_day': avg_volume,
        'min_sell_price': min_sell,
        'max_buy_price': max_buy,
        'total_sell_volume': total_sell_volume,
        'total_buy_volume': total_buy_volume
    }


def get_top_traded_items(region_id, station_id, top_n=100):
    """Orchestre le traitement complet : top items vendus avec données marché."""
    type_ids = get_all_type_ids(region_id)
    
    avg_volumes = []
    total = len(type_ids)
    for i, type_id in enumerate(type_ids, 1):
        avg_volume = get_average_volume_per_day(region_id, type_id)
        if avg_volume > 0:
            avg_volumes.append((type_id, avg_volume))
        print(f"  -> progression {i}/{total}", end='\r')
        time.sleep(0.1)  # Garde le sleep pour pas spammer trop l'API

    print("  ✓  Calcul volumes terminé")

    top_items = sorted(avg_volumes, key=lambda x: x[1], reverse=True)[:top_n]
    sell_orders = get_market_orders(region_id, 'sell')
    buy_orders = get_market_orders(region_id, 'buy')

    print(f"  -> Récupération des ordres terminée, traitement des {len(top_items)} top items...")

    result = []
    total_top = len(top_items)
    for i, (type_id, avg_volume) in enumerate(top_items, 1):
        summary = summarize_item_market_data(type_id, region_id, station_id, avg_volume, sell_orders, buy_orders)
        result.append(summary)
        print(f"  -> progression {i}/{total_top}", end='\r')

    print("  ✓  Résumé des items terminé")
    return result