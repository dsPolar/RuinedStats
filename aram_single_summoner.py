from riotwatcher import LolWatcher, ApiError
import pandas as pd
import numpy as np
import time
from api_key import key




def get_last_hundred_matches(region, user, queue_id, lol_watcher):
    try:
        last_hundred_aram = lol_watcher.match.matchlist_by_account(region, user['accountId'], queue=queue_id, begin_index=0, end_index=100)
    except ApiError as err:
        raise


    summoner_game_frame = pd.DataFrame.from_dict(last_hundred_aram['matches'])
    summoner_game_frame = summoner_game_frame.drop(["platformId", "queue", ], axis=1)

    game_dict = {"matches":[]}

    for row in summoner_game_frame.itertuples(index=False, name="Games"):
        try:
            game = lol_watcher.match.by_id(region, row.gameId)

            game_dict['matches'].append(game)
        except ApiError as err:
            raise

    # Dataframe containing MatchDto objects
    game_frame = pd.DataFrame.from_dict(game_dict['matches'])

    game_frame.to_csv("csv/my_aram_games.csv")

def get_all_arams(region, user, lol_watcher):
    begin_index = 0
    not_done = True
    all_aram_dict = {"matches":[]}
    while not_done:
        try:
            hundred_aram = lol_watcher.match.matchlist_by_account(region, user['accountId'], queue="450", begin_index=begin_index)
        except ApiError as err:
                raise
        for game in hundred_aram['matches']:
            all_aram_dict['matches'].append(game)



        # If there are less than 100 games in the response then we assume we have reached the end of the history
        # While the response includes a total_games variable, the api requests to use this method instead
        if(len(hundred_aram['matches']) < 100):
            not_done = False
        else:
            begin_index += 100

    all_aram_frame = pd.DataFrame.from_dict(all_aram_dict['matches'])
    # all_aram_frame should now contain all arams since queue id changed >patch 7.19
    print(str(len(all_aram_frame.index)) + " Total Games Found")
    all_aram_frame = all_aram_frame.drop(['platformId', 'queue', 'timestamp'], axis=1)

    all_aram_frame.to_csv("csv/all_aram_games.csv")



if __name__ == "__main__":
    lol_watcher = LolWatcher(key)

    region = "euw1"

    queue_id = "450"

    user = lol_watcher.summoner.by_name(region, "CatgirlViegoGF")

    get_all_arams(region, user, lol_watcher)
