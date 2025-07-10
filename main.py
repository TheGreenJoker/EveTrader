import downloader as d
import jsoner as j
import analyser as a


def analyse_from_web(min_profit_percent, min_volume_per_day, region_id=10000002, station_id=60003760, top_n=100, json=(True, "data.json")):
    save, json_filename = json
    
    print("📥 Téléchargement des données du marché...")
    items = d.get_top_traded_items(region_id, station_id, top_n=top_n)
    
    if save:
        print(f"💾 Sauvegarde des {len(items)} items dans le fichier JSON...")
        j.save_items_to_json(items, json_filename)

    print(f"🔎 Application des filtres : profit > {min_profit_percent}%, volume > {min_volume_per_day} items/jour...")
    filtered_items = a.filter_items(items, min_profit_percent, min_volume_per_day)

    print(f"✅ {len(filtered_items)} items correspondent aux critères :\n")
    a.print_filtered_items(filtered_items)


def analyse_from_local(min_profit_percent, min_volume_per_day, json_filename):
    print(f"📥 Chargement du fichier JSON...")
    items = j.load_items_from_json(json_filename)

    print(f"🔎 Application des filtres : profit > {min_profit_percent}%, volume > {min_volume_per_day} items/jour...")
    filtered_items = a.filter_items(items, min_profit_percent, min_volume_per_day)

    print(f"✅ {len(filtered_items)} items correspondent aux critères :\n")
    a.print_filtered_items(filtered_items)



if __name__ == "__main__":
    min_profit_percent = 0.0
    min_volume_per_day = 0
    fetch_data = False

    if fetch_data:
        analyse_from_web(min_profit_percent, min_volume_per_day, (True, "test.json"))
    else:
        analyse_from_local(min_profit_percent, min_volume_per_day, "top_100_items_jita.json")