import json

def load_json(filepath):
    """Charge un fichier JSON."""
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)


def save_json(data, filepath):
    """Sauvegarde les données dans un fichier JSON."""
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

