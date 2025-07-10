import requests
import time

_item_name_cache = {}

def get_item_name(type_id):
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
    url = f"https://esi.evetech.net/latest/markets/{region_id}/types/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_market_history(region_id, type_id, days=7):
    url = f"https://esi.evetech.net/latest/markets/{region_id}/history/?type_id={type_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    return response.json()[-days:]  # derniers jours


def estimate_bought_vs_sold(history, min_sell_price, max_buy_price, tolerance=0.02):
    volume_bought = 0
    volume_sold = 0

    for day in history:
        price = day['average']
        volume = day['volume']
        if min_sell_price and abs(price - min_sell_price) / min_sell_price <= tolerance:
            volume_bought += volume
        elif max_buy_price and abs(price - max_buy_price) / max_buy_price <= tolerance:
            volume_sold += volume
        else:
            # Ignoré si on ne peut pas l’attribuer de manière fiable
            pass

    return volume_bought / len(history), volume_sold / len(history)


def get_average_volume_per_day(region_id, type_id, days=7):
    history = get_market_history(region_id, type_id, days)
    if not history:
        return 0
    return sum(day['volume'] for day in history) / len(history)


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
    print(f"  ✓  {order_type} orders retrieved")
    return orders


def filter_orders_by_item_and_station(orders, type_id, station_id):
    return [o for o in orders if o['type_id'] == type_id and o['location_id'] == station_id]


def summarize_item_market_data(type_id, region_id, station_id, avg_volume, sell_orders, buy_orders):
    sell_filtered = filter_orders_by_item_and_station(sell_orders, type_id, station_id)
    buy_filtered = filter_orders_by_item_and_station(buy_orders, type_id, station_id)

    min_sell = min([o['price'] for o in sell_filtered], default=None)
    max_buy = max([o['price'] for o in buy_filtered], default=None)
    total_sell_volume = sum([o['volume_remain'] for o in sell_filtered])
    total_buy_volume = sum([o['volume_remain'] for o in buy_filtered])

    history = get_market_history(region_id, type_id, days=7)
    avg_bought, avg_sold = estimate_bought_vs_sold(history, min_sell, max_buy)

    return {
        'type_id': type_id,
        'avg_volume_per_day': avg_volume,
        'avg_daily_bought': avg_bought,
        'avg_daily_sold': avg_sold,
        'min_sell_price': min_sell,
        'max_buy_price': max_buy,
        'total_sell_volume': total_sell_volume,
        'total_buy_volume': total_buy_volume,
    }


def get_top_traded_items(region_id, station_id, top_n=100):
    type_ids = get_all_type_ids(region_id)
    
    avg_volumes = []
    total = len(type_ids)
    for i, type_id in enumerate(type_ids, 1):
        avg_volume = get_average_volume_per_day(region_id, type_id)
        if avg_volume > 0:
            avg_volumes.append((type_id, avg_volume))
        print(f"  -> progression {i}/{total}", end='\r')
        time.sleep(0.1)

    print("  ✓  Average volume calculation complete")

    top_items = sorted(avg_volumes, key=lambda x: x[1], reverse=True)[:top_n]
    sell_orders = get_market_orders(region_id, 'sell')
    buy_orders = get_market_orders(region_id, 'buy')

    print(f"  -> Processing top {len(top_items)} items...")

    result = []
    for i, (type_id, avg_volume) in enumerate(top_items, 1):
        summary = summarize_item_market_data(type_id, region_id, station_id, avg_volume, sell_orders, buy_orders)
        result.append(summary)
        print(f"  -> progression {i}/{len(top_items)}", end='\r')

    print("  ✓  Item summaries complete")
    return result
