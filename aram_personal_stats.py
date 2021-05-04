from riotwatcher import LolWatcher, ApiError
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from api_key import key
import aram_single_summoner
from data_dragon_handler import create_champion_id_dict

if __name__ == "__main__":
    frame = pd.read_csv("csv/all_aram_games.csv", index_col=0)
    champion_ids_dict = create_champion_id_dict()
    frame["champion"] = frame["champion"].astype(str)

    frame.replace({"champion": champion_ids_dict}, inplace=True)

    # Get frequency of champion occurence
    champion_counts = frame['champion'].value_counts().to_dict()
    with open("output/champion_counts.txt", "w") as f:
        print(champion_counts, file=f)
        f.close()

    # Create dataframe in the format we want
    champion_playrate_frame = pd.DataFrame.from_dict({"name":list(champion_ids_dict.values())})

    # Find the champions that haven't been played in the range
    unplayed_champions = [champ for champ in list(champion_ids_dict.values()) if champ not in list(champion_counts.keys())]

    # Dictionary comprehension to create a name:gameCount pair for each unplayed champion
    champion_counts.update({key:0 for key in unplayed_champions})

    # Add the gameCount column with the champion name mapped to their playcount
    champion_playrate_frame['gameCount'] = champion_playrate_frame['name'].map(champion_counts)

    expected_playrate = 1.0 / len(champion_ids_dict.keys())
    total_games = len(frame.index)

    champion_playrate_frame['playrate'] = champion_playrate_frame['gameCount'] / total_games
    champion_playrate_frame['playrateDelta'] = champion_playrate_frame['playrate'] - expected_playrate

    champion_playrate_frame['playratePercent'] = pd.Series(["{0:.2f}%".format(val * 100) for val in champion_playrate_frame['playrate']],index = champion_playrate_frame.index)
    champion_playrate_frame['playrateDeltaPercent'] = pd.Series(["{0:.2f}%".format(val * 100) for val in champion_playrate_frame['playrateDelta']],index = champion_playrate_frame.index)

    print(champion_playrate_frame.sort_values(by='playratePercent', ascending=False, axis='index')[:10])
    print(champion_playrate_frame.sort_values(by='playratePercent', axis='index')[:10])
