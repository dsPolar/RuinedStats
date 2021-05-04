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
    champion_counts = frame['champion'].value_counts()
    with open("output/champion_counts.txt", "w") as f:
        print(champion_counts.to_string(), file=f)
        f.close()
