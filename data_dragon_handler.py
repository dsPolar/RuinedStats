import json

def load_champion_json():
    with open('data_dragon/champion.json', 'r') as f:
        champions = json.load(f)
        f.close()
    return champions['data']

def create_champion_id_dict(champion=load_champion_json()):
    champion_ids = {}

    for champ in champion.values():
        champion_ids.update({champ['key'] : champ['id']})
    return champion_ids
