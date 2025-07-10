import downloader as d
import jsoner as j
import analyser as a
import tools as t

def analyse_from_web(min_profit_percent, min_volume_per_day, region_id=10000002, station_id=60003760, top_n=100, json=(True, "data.json")):
    save, json_filename = json
    
    print("📥 Downloading market data...")
    items = d.get_top_traded_items(region_id, station_id, top_n=top_n)
    
    if save:
        print(f"💾 Saving {len(items)} items to JSON file...")
        j.save_items_to_json(items, json_filename)

    print(f"🔎 Applying filters: profit > {min_profit_percent}%, volume > {min_volume_per_day} items/day...")
    filtered_items = a.filter_items(items, min_profit_percent, min_volume_per_day)

    print(f"✅ {len(filtered_items)} items match criteria:\n")
    a.print_filtered_items(filtered_items)


def analyse_from_local(min_profit_percent, min_volume_per_day, json_filename):
    print(f"📥 Loading JSON file...")
    items = j.load_items_from_json(json_filename)

    print(f"🔎 Applying filters: profit > {min_profit_percent}%, volume > {min_volume_per_day} items/day...")
    filtered_items = a.filter_items(items, min_profit_percent, min_volume_per_day)

    print(f"✅ {len(filtered_items)} items match criteria:\n")
    a.print_filtered_items(filtered_items)


if __name__ == "__main__":
    print("=== EVE Online Market Analyzer ===")

    min_profit_percent = t.ask_input("Minimum profit percent", 20.0, float)
    min_volume_per_day = t.ask_input("Minimum volume per day", 100, int)
    region_id = t.ask_input("Region ID", 10000002, int)
    station_id = t.ask_input("Station ID", 60003760, int)
    top_n = t.ask_input("Number of top items to analyze", 100, int)
    fetch_data = t.ask_yes_no("Fetch data from web?")

    json_save = (False, "")
    if fetch_data:
        save_json = t.ask_yes_no("Save data to JSON file?")
        json_filename = "data.json"
        if save_json:
            json_filename = input("Enter JSON filename [data.json]: ").strip() or "data.json"
        json_save = (save_json, json_filename)
        print("\n=== EVE Online Market Analyzer ===\n")
        analyse_from_web(min_profit_percent, min_volume_per_day, region_id, station_id, top_n, json_save)
    else:
        json_filename = input("Enter JSON filename to load [top_100_items_jita.json]: ").strip() or "top_100_items_jita.json"
        print("\n=== EVE Online Market Analyzer ===\n")
        analyse_from_local(min_profit_percent, min_volume_per_day, json_filename)
