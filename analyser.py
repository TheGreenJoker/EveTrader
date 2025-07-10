from downloader import get_item_name


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
    Displays the list of filtered items as a formatted table with names.
    """

    widths = {
        'type_id': 10,
        'name': 30,
        'profit_percent': 10,
        'volume': 12,
        'min_sell_price': 15,
        'max_buy_price': 15
    }

    header = (
        f"{'Type ID':<{widths['type_id']}} | "
        f"{'Name':<{widths['name']}} | "
        f"{'Profit %':>{widths['profit_percent']}} | "
        f"{'Volume/day':>{widths['volume']}} | "
        f"{'Min Sell Price':>{widths['min_sell_price']}} | "
        f"{'Max Buy Price':>{widths['max_buy_price']}}"
    )
    print(header)
    print('-' * len(header))

    for item in items:
        type_id = item.get('type_id', 'N/A')
        name = get_item_name(type_id)
        profit = item.get('profit_percent', 0.0)
        volume = int(item.get('avg_volume_per_day', 0))
        min_sell = item.get('min_sell_price', 'N/A')
        max_buy = item.get('max_buy_price', 'N/A')

        line = (
            f"{str(type_id):<{widths['type_id']}} | "
            f"{name[:widths['name']]:<{widths['name']}} | "
            f"{profit:>{widths['profit_percent']}.2f} | "
            f"{volume:>{widths['volume']}} | "
            f"{min_sell:>{widths['min_sell_price']}} | "
            f"{max_buy:>{widths['max_buy_price']}}"
        )
        print(line)

    print()
