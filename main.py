import downloader as d
import jsoner as j
import analyser as a

def main():
    region_id = 10000002       # The Forge
    station_id = 60003760      # Jita 4-4
    top_n = 100
    json_filename = "top_100_items_jita.json"

    min_profit_percent = 10.0
    min_volume_per_day = 10000

    print("📥 Téléchargement des données du marché...")
    items = d.get_top_traded_items(region_id, station_id, top_n=top_n)
    
    print(f"💾 Sauvegarde des {len(items)} items dans le fichier JSON...")
    j.save_items_to_json(items, json_filename)

    print(f"🔎 Application des filtres : profit > {min_profit_percent}%, volume > {min_volume_per_day} items/jour...")
    filtered_items = a.filter_items(items, min_profit_percent, min_volume_per_day)

    print(f"✅ {len(filtered_items)} items correspondent aux critères :\n")
    a.print_filtered_items(filtered_items)


if __name__ == "__main__":
    main()
