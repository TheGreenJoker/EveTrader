def calculate_profit_percent(item):
    """
    Calcule le profit en % entre ordre d'achat max et ordre de vente min.
    Retourne None si pas possible.
    """
    min_sell = item['min_sell_price']
    max_buy = item['max_buy_price']
    
    if min_sell is None or max_buy is None or min_sell == 0:
        return None
    return ((min_sell / max_buy) - 1) * 100


def filter_by_profit(items, min_profit_percent):
    """
    Filtre les items dont le profit est supérieur à min_profit_percent.
    Calcule aussi et ajoute la clé 'profit_percent' dans chaque item.
    """
    filtered = []
    for item in items:
        profit = calculate_profit_percent(item)
        if profit is not None and profit > min_profit_percent:
            item['profit_percent'] = profit
            filtered.append(item)
    return filtered


def filter_by_volume(items, min_volume_per_day):
    """
    Filtre les items dont le volume vendu par jour est supérieur au seuil.
    """
    return [item for item in items if item['avg_volume_per_day'] > min_volume_per_day]


def filter_items(items, min_profit_percent, min_volume_per_day):
    """
    Applique les filtres profit et volume ensemble.
    """
    filtered_profit = filter_by_profit(items, min_profit_percent)
    filtered_final = filter_by_volume(filtered_profit, min_volume_per_day)
    return filtered_final


def print_filtered_items(items):
    """
    Affiche la liste filtrée de manière lisible.
    """
    for item in items:
        print(f"Type ID: {item['type_id']} | "
              f"Profit: {item.get('profit_percent', 0):.2f}% | "
              f"Volume/jour: {item.get('avg_volume_per_day', 0):.0f} | "
              f"Sell Price: {item.get('min_sell_price')} | "
              f"Buy Price: {item.get('max_buy_price')}")
