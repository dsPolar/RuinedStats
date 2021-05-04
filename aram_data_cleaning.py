from riotwatcher import LolWatcher, ApiError
import pandas as pd
import numpy as np


from api_key import key
import aram_single_summoner




def load_frame(path="csv/aram_games_info.csv"):
    return pd.read_csv(path, index_col=0)


def save_frame(aram_frame, path="csv/aram_games_info.csv"):
    aram_frame.to_csv(path)

def drop_unnamed(aram_frame):
    return aram_frame.drop(aram_frame.columns[aram_frame.columns.str.contains('unnamed', case = False)], axis=1)

def drop_needless(aram_frame):
    return aram_frame.drop(['platformId', 'queueId', 'mapId', 'gameMode', 'gameType'], axis=1)

if __name__ == "__main__":
    aram_frame = load_frame()
    #aram_frame = drop_unnamed(aram_frame)
    aram_frame = drop_needless(aram_frame)

    save_frame = save_frame(aram_frame)
