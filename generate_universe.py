import requests
import json
import time

BASE_URL = "https://esi.evetech.net/latest"

HEADERS = {"Accept": "application/json"}

def get_regions():
    res = requests.get(f"{BASE_URL}/universe/regions/", headers=HEADERS)
    return res.json()

def get_region_info(region_id):
    res = requests.get(f"{BASE_URL}/universe/regions/{region_id}/", headers=HEADERS)
    return res.json()

def get_region_systems(region_id):
    res = requests.get(f"{BASE_URL}/universe/regions/{region_id}/", headers=HEADERS)
    return res.json().get("systems", [])

def get_system_info(system_id):
    res = requests.get(f"{BASE_URL}/universe/systems/{system_id}/", headers=HEADERS)
    return res.json()

def get_station_info(station_id):
    res = requests.get(f"{BASE_URL}/universe/stations/{station_id}/", headers=HEADERS)
    return res.json()

def get_stations_in_region(region_id):
    url = f"{BASE_URL}/universe/stations/?datasource=tranquility"
    all_stations = requests.get(url, headers=HEADERS).json()

    region_stations = {}
    for station_id in all_stations:
        try:
            station = get_station_info(station_id)
            if station.get("region_id") == region_id:
                system_id = station.get("system_id")
                if system_id not in region_stations:
                    region_stations[system_id] = {}
                region_stations[system_id][station_id] = station.get("name")
            time.sleep(0.1)  # avoid API rate limit
        except Exception:
            continue
    return region_stations

def build_universe():
    universe = {}
    regions = get_regions()

    for region_id in regions:
        try:
            region_info = get_region_info(region_id)
            systems = get_region_systems(region_id)
            stations_by_system = get_stations_in_region(region_id)

            region_data = {
                "name": region_info.get("name"),
                "systems": {}
            }

            for system_id in systems:
                try:
                    system_info = get_system_info(system_id)
                    region_data["systems"][str(system_id)] = {
                        "name": system_info.get("name"),
                        "stations": stations_by_system.get(system_id, {})
                    }
                    time.sleep(0.1)
                except Exception:
                    continue

            universe[str(region_id)] = region_data
            print(f"✔ Region {region_data['name']} processed.")
        except Exception as e:
            print(f"❌ Failed region {region_id}: {e}")
        time.sleep(0.5)

    return universe


if __name__ == "__main__":
    print("📡 Building universe...")
    universe = build_universe()

    with open("static/data/universe.json", "w") as f:
        json.dump(universe, f, indent=2)

    print("✅ Universe saved to static/data/universe.json")
