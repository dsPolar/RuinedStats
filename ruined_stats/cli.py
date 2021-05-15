

import sys

from riotwatcher import LolWatcher

import ruined_stats.config
from ruined_stats import persister
from ruined_stats.models import Session

summoner_name = sys.argv[1]


def get_player_by_summoner_name(summoner_name):
    lol_watcher = LolWatcher(ruined_stats.config.key)

    region = "euw1"
    queue_id = "450"

    user = lol_watcher.summoner.by_name(region, summoner_name)
    return user


def save_player_by_summoner_name(summoner_name):
    session = Session()
    player = get_player_by_summoner_name(summoner_name)
    persister.create_player(session, player)





player = save_player_by_summoner_name(summoner_name)
print(player)
