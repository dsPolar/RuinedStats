import sys

from riotwatcher import LolWatcher

import ruined_stats.config
from ruined_stats import persister
from ruined_stats.models import Session
from ruined_stats.models import get_unscraped_player

summoner_name = sys.argv[1]


def get_player_by_summoner_name(summoner_name):
    lol_watcher = LolWatcher(ruined_stats.config.key)

    user = lol_watcher.summoner.by_name(ruined_stats.config.region, summoner_name)
    return user


def save_player_by_summoner_name(summoner_name):
    session = Session()
    player = get_player_by_summoner_name(summoner_name)
    persister.get_or_create_player(session, player)
    return player


def get_match_info_by_id(match_id):
    lol_watcher = LolWatcher(ruined_stats.config.key)
    match_info = lol_watcher.match.by_id(ruined_stats.config.region, match_id)
    teams = match_info["teams"]
    participants = match_info["participants"]
    participant_identities = match_info["participantIdentities"]
    return match_id, teams, participants, participant_identities


def save_match_info_by_id(match_id):
    session = Session()
    match, teams, participants, participant_identities = get_match_info_by_id(match_id)
    persister.create_match(session, match, teams, participants, participant_identities)


def save_matchlist(matchlist):
    for match in matchlist:
        save_match_info_by_id(match["gameId"])


def get_and_save_matchlist_by_account_id(sql_player, account_id):
    lol_watcher = LolWatcher(ruined_stats.config.key)
    # Work out some solution to get id's for all games
    begin_index = 0
    done = False
    while not done:
        matchlist_response = lol_watcher.match.matchlist_by_account(ruined_stats.config.region, account_id,
                                                                    queue=ruined_stats.config.queue_id,
                                                                    begin_index=begin_index
                                                                    )
        if len(matchlist_response["matches"]) < 100:
            done = True
        save_matchlist(matchlist_response["matches"])
    if done:
        persister.update_player_scraped(sql_player, True)


def scrape_unscraped_player():
    sql_player = get_unscraped_player()
    try:
        get_and_save_matchlist_by_account_id(sql_player, sql_player.account_id)
    except Exception as e:
        print(e)


player = save_player_by_summoner_name(summoner_name)
print(player)
