import json


def save_items_to_json(items_data, filename="top_items.json"):
    """
    Sauvegarde une liste d’items dans un fichier JSON.
    
    :param items_data: Liste de dictionnaires avec les infos par item
    :param filename: Nom du fichier de sortie (par défaut "top_items.json")
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(items_data, f, ensure_ascii=False, indent=4)
    print(f"{len(items_data)} items enregistrés dans '{filename}'")


def load_items_from_json(filename="top_items.json"):
    import json
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)
