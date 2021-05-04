from riotwatcher import LolWatcher, ApiError
import pandas as pd
import numpy as np

from api_key import key


# Make a request to matchv4 api through riot watcher
# Make several attempts to achieve result in case of timeouts
def game_info_request(region, game_id, lol_watcher, num_retries=3):
    for num_attempt in range(num_retries):
        try:
            game_info = lol_watcher.match.by_id(region, game_id)
            return game_info
        except ApiError as err:
            if err.response.status_code == 400:
                print("Bad Request")
                raise
            elif num_attempt < (num_retries - 1):
                print("Failed to receive response")
                print(str(err.response.status_code))
            else:
                raise

# Get up to 100 matches in queue for user
# Defaults to recency but begin_index can be used to navigate further back
def get_hundred_matches(region, user, queue_id, lol_watcher, begin_index=0):
    try:
        last_hundred_aram = lol_watcher.match.matchlist_by_account(region, user['accountId'], queue=queue_id, begin_index=begin_index)
    except ApiError as err:
        raise


    summoner_game_frame = pd.DataFrame.from_dict(last_hundred_aram['matches'])
    summoner_game_frame = summoner_game_frame.drop(["platformId", "queue", ], axis=1)

    game_dict = {"matches":[]}

    for row in summoner_game_frame.itertuples(index=False, name="Games"):
        try:
            game = game_info_request(region, row.gameId, lol_watcher)

            game_dict['matches'].append(game)
        except ApiError as err:
            raise

    # Dataframe containing MatchDto objects
    game_frame = pd.DataFrame.from_dict(game_dict['matches'])

    game_frame.to_csv("csv/aram_games_begin_" + str(begin_index) + ".csv")
    return game_frame

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
    return all_aram_frame

def load_arams():
    df = pd.read_csv("csv/all_aram_games.csv")
    return df

def concat_aram_game_info_frames(path):
    frames = []
    for x in range(0,1500,100):
        frames.append(pd.read_csv(path + str(x) + ".csv"))
    total_frame = pd.concat(frames)
    total_frame.to_csv(path + "all.csv")
    return total_frame

def get_full_game_info_for_frame(match_frame, region, lol_watcher):

    game_dict = {'matches':[]}

    for row in match_frame.itertuples(index=False, name='Games'):
        try:
            game = lol_watcher.match.by_id(region, row.gameId)
            game_dict['matches'].append(game)
        except ApiError as err:
            raise

    full_game_frame = pd.DataFrame.from_dict(game_dict['matches'])

    full_game_frame.to_csv("csv/all_aram_full_game_info.csv")
    return full_game_frame



if __name__ == "__main__":
    lol_watcher = LolWatcher(key)

    region = "euw1"

    queue_id = "450"

    user = lol_watcher.summoner.by_name(region, "CatgirlViegoGF")

    #get_all_arams(region, user, lol_watcher)

    #match_frame = load_arams()
    #full_game_frame = get_full_game_info_for_frame(match_frame, region, lol_watcher)

    #for begin_index in range(1400,1500,100):
    #    get_hundred_matches(region, user, queue_id, lol_watcher, begin_index=begin_index)

    #concat_aram_game_info_frames("csv/aram_games_begin_")
