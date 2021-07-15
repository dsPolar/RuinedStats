import sys
from typing import Any, Tuple

from riotwatcher import ApiError
from sqlalchemy.sql import ClauseElement

from ruined_stats import models, cli

def get_or_create_with_object(session, model, sql_object, **kwargs):
    instance = session.query(model).filter_by(**kwargs).one_or_none()
    if instance:
        # Item exists in table already
        return instance, False
    else:
        try:
            session.add(sql_object)
            session.commit()
        except Exception:
            session.rollback()
            instance = session.query(model).filter_by(**kwargs).one()
            return instance, False
        else:
            return sql_object, True

def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).one_or_none()
    if instance:
        return instance, False
    else:
        params = {k: v for k, v in kwargs.items() if not isinstance(v, ClauseElement)}
        params.update(defaults or {})
        instance = model(**params)
        try:
            session.add(instance)
            session.commit()
        except Exception:  # The actual exception depends on the specific database so we catch all exceptions. This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
            session.rollback()
            instance = session.query(model).filter_by(**kwargs).one()
            return instance, False
        else:
            return instance, True


def create_match(session, riot_match_id, teams, participants, participant_identities):
    # Should check if match exists already
    # Skip process if it does
    match_check = session.query(models.Match).filter_by(riot_match_id=riot_match_id).one_or_none()
    if not match_check:
        match: Tuple[Any, bool] = get_or_create(session, models.Match, defaults=dict(), riot_match_id=riot_match_id)
        print("Added match with internal id " + str(match[0].match_id) + " and rito id " + str(riot_match_id))
        # Now need to get team stats info
        team_stats_objects = []
        for i in range(len(teams)):
            team_stats_objects.append(dict())

        def map_win_to_bool(win_string):
            if win_string == "Win":
                return True
            else:
                return False

        assert len(teams) == 2
        for i, team in enumerate(teams):
            team_stats_objects[i]["team_id"] = team["teamId"]
            team_stats_objects[i]["first_blood"] = team["firstBlood"]
            team_stats_objects[i]["first_tower"] = team["firstTower"]
            team_stats_objects[i]["first_inhib"] = team["firstInhibitor"]
            team_stats_objects[i]["win"] = map_win_to_bool(team["win"])

            team_stats_objects[i]["object"] = get_or_create(session, models.TeamStats, defaults=dict(
                first_blood=team_stats_objects[i]["first_blood"],
                first_tower=team_stats_objects[i]["first_tower"],
                first_inhib=team_stats_objects[i]["first_inhib"],
                win=team_stats_objects[i]["win"]
            ),
                match_id=match[0].match_id,
                team_id=team_stats_objects[i]["team_id"])
            print("Created TeamStats object with internal id " + str(team_stats_objects[i]["object"][0].team_stats_id))

        # Now need to get the player information
        player_objects = []
        for i in range(len(participant_identities)):
            player_objects.append(dict())
        assert len(participants) == len(participant_identities)

        for i in range(len(participant_identities)):
            # Check summonerId against database and get or create object
            # Keep objects to have id to link to

            # Player format within match participant identities is non ideal as it doesn't have puuid
            # So instead call summoner api by the account id to get better data

            # However seemingly the call by account id can fail, maybe changed region? or summoner name?
            # So try account first, then name, then just create with empty puuid and mark as scraped so
            # we never touch it
            """
            temp_player = None
            try:
                temp_player = cli.get_player_by_account_id(participant_identities[i]["player"]["accountId"])
            except ApiError as err:
                if err.response.status_code == 404:
                    try:
                        temp_player = cli.get_player_by_summoner_name(participant_identities[i]["player"]["summonerName"])
                    except ApiError as err2:
                        if err.response.status_code == 404:
                            temp_player = None
            if temp_player is not None:
                player_objects[i]["object"] = get_or_create_player(session, temp_player)
            else:
                player_objects[i]["object"] = get_or_create_null_player(session, participant_identities[i]["player"])
            """
            player_objects[i]["object"] = get_or_create_player_from_match_participant(session, participant_identities[i]["player"])

            player_objects[i]["team_participant_id"] = participant_identities[i]["participantId"]
            player_objects[i]["team_id"] = \
                next(item for item in participants if item["participantId"] == player_objects[i]["team_participant_id"])["teamId"]

            # Find the list element with id we want, and get the champion_id from that
            player_objects[i]["champion_id"] = \
                next(item for item in participants if item["participantId"] == player_objects[i]["team_participant_id"])["championId"]

            player_objects[i]["participant_object"] = get_or_create(session, models.Participant, defaults=dict(
                team_participant_id=player_objects[i]["team_participant_id"],
                champion_id=player_objects[i]["champion_id"]
            ),
                player_id=player_objects[i]["object"][0].player_id,
                team_stats_id=next(item for item in team_stats_objects if item["team_id"] == player_objects[i]["team_id"])["object"][0].team_stats_id
            )

def get_or_create_player(session, player):
    player_object = get_or_create(session, models.Player, defaults=dict(
        summoner_id=player["id"],
        puuid=player["puuid"]
    ), account_id=player["accountId"])
    print("Created player object for account id " + str(player_object[0].account_id))
    return player_object

def get_or_create_player_from_match_participant(session, player):
    player_object = get_or_create(session, models.Player, defaults=dict(
        summoner_id=player["summonerId"],
        puuid=player["accountId"] + "NULLPUUID"
    ), account_id=player["accountId"])
    print("Created player object for account id " + str(player_object[0].account_id))
    return player_object

def get_or_create_null_player(session, player_from_match):
    player_object = get_or_create(session, models.Player, defaults=dict(
        summoner_id=player_from_match["summonerId"],
        puuid=player_from_match["accountId"] + "NULLPUUID",
        scraped=True
    ), account_id=player_from_match["accountId"])
    print("Created null player object for account id " + str(player_object[0].account_id))
    return player_object

def update_player_scraped(session, sql_player, new_scraped):
    sql_player.scraped = new_scraped
    session.commit()
