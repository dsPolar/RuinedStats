import sys
from typing import Optional, Any

from riotwatcher import LolWatcher, ApiError

from ruined_stats import config
from ruined_stats import persister
from ruined_stats.models import Session, get_unscraped_player


def get_player_by_summoner_name(summoner_name):
    lol_watcher = LolWatcher(config.key)

    user = lol_watcher.summoner.by_name(config.region, summoner_name)
    return user

def get_player_by_account_id(account_id):
    lol_watcher = LolWatcher(config.key)
    user = lol_watcher.summoner.by_account(config.region, account_id)
    return user

def save_player_by_summoner_name(summoner_name):
    session = Session()
    player = get_player_by_summoner_name(summoner_name)
    persister.get_or_create_player(session, player)
    return player


def get_match_info_by_id(match_id):
    lol_watcher = LolWatcher(config.key)
    for attempt in range(config.number_of_retries):
        try:
            match_info = lol_watcher.match.by_id(config.region, match_id)
            teams = match_info["teams"]
            participants = match_info["participants"]
            participant_identities = match_info["participantIdentities"]
        except ApiError as err:
            if attempt < (config.number_of_retries - 1):
                print(err)
                print("ApiError within retry count. Retrying...")
            else:
                raise
    return match_id, teams, participants, participant_identities


def save_match_info_by_id(match_id):
    session = Session()
    match, teams, participants, participant_identities = get_match_info_by_id(match_id)
    persister.create_match(session, match, teams, participants, participant_identities)


def save_matchlist(matchlist):
    for match in matchlist:
        save_match_info_by_id(match["gameId"])


def get_and_save_matchlist_by_account_id(sql_player, account_id):
    lol_watcher = LolWatcher(config.key)
    session = Session()
    # Work out some solution to get id's for all games
    begin_index = 0
    done = False
    while not done:
        matchlist_response = lol_watcher.match.matchlist_by_account(config.region, account_id,
                                                                    queue=config.queue_id,
                                                                    begin_index=begin_index
                                                                    )
        print(str(len(matchlist_response["matches"])))
        if len(matchlist_response["matches"]) < 100:
            print("Updating scraped to true")
            persister.update_player_scraped(session, sql_player, True)
            done = True
        save_matchlist(matchlist_response["matches"])
        begin_index += 100
    return


def scrape_player(sql_player):
    print("Scraping " + str(sql_player.account_id))
    get_and_save_matchlist_by_account_id(sql_player, sql_player.account_id)

def scraping_procedure(number_of_users_to_scrape):
    for i in range(number_of_users_to_scrape):
        sql_player = get_unscraped_player()
        if sql_player is not None:
            scrape_player(sql_player)
        else:
            if i == 0:
                session = Session()
                summoner = get_player_by_summoner_name(config.bootstrap_summoner_name)
                sql_player = persister.get_or_create_player(session, summoner)
                scrape_player(sql_player)
            else:
                raise RuntimeError("No unscraped players in database after bootstrap scraped")


if __name__ == "__main__":
    try:
        scrape_count = int(sys.argv[1])
    except IndexError:
        scrape_count = 1

    try:
        scraping_procedure(scrape_count)
    except RuntimeError as err:
        print(err)
