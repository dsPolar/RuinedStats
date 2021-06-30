
import sys

from riotwatcher import LolWatcher

import ruined_stats.config
from ruined_stats import persister
from ruined_stats.models import Session

summoner_name = sys.argv[1]


def get_player_by_summoner_name(summoner_name):
    lol_watcher = LolWatcher(ruined_stats.config.key)

    user = lol_watcher.summoner.by_name(ruined_stats.config.region, summoner_name)
    return user


def save_player_by_summoner_name(summoner_name):
    session = Session()
    player = get_player_by_summoner_name(summoner_name)
    persister.create_player(session, player)

def get_match_info_by_id(match_id):
    lol_watcher = LolWatcher(ruined_stats.config.key)
    match_info = lol_watcher.match.by_id(ruined_stats.config.region, match_id)
    teams = match_info["teams"]
    players = match_info["participants"]
    return match_id, teams, players

def save_match_info_by_id(match_id):
    session = Session()
    match, teams, players = get_match_info_by_id(match_id)
    persister.create_match(session, match, teams, players)



player = save_player_by_summoner_name(summoner_name)
print(player)
