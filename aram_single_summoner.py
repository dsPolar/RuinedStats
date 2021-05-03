from riotwatcher import LolWatcher, ApiError
import pandas as pd
import numpy as np
import time
from api_key import key


lol_watcher = LolWatcher(key)

region = "euw1"

queue_id = "450"

user = lol_watcher.summoner.by_name(region, "CatgirlViegoGF")

try:
    last_hundred_aram = lol_watcher.match.matchlist_by_account(region, user['accountId'], queue=queue_id, begin_index=0, end_index=100)
except ApiError as err:
    raise


summoner_game_frame = pd.DataFrame.from_dict(last_hundred_aram['matches'])
summoner_game_frame = summoner_game_frame.drop(["platformId", "queue", ], axis=1)

game_dict = {"matches":[]}

for row in summoner_game_frame.itertuples(index=False, name="Games"):
    #Sleep for 200ms to make sure we don't hit the request limit
    #time.sleep(0.2)
    try:
        game = lol_watcher.match.by_id(region, row.gameId)

        game_dict['matches'].append(game)
    except ApiError as err:
        raise

# Dataframe containing MatchDto objects
game_frame = pd.DataFrame.from_dict(game_dict['matches'])

game_frame.to_csv("my_aram_games.csv")

def get_all_arams(region, user):
    begin_index = 0
    not_done = True
    while not_done:
        try:
            hundred_aram = lol_watcher.match.matchlist_by_account(region, user['accountId'], queue="450", begin_index=begin_index)
        except ApiError as err:
            if err.response.status_code == 400:
                print("Error 400, bad request, likely 0 games in filter")
            else:
                raise
