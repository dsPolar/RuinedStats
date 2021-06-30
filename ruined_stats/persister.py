from sqlalchemy.sql import ClauseElement

from ruined_stats import models


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


def create_match(session, match_id, teams, participants):
    # Get the instance we just created to use the primary key
    match = get_or_create(session, models.Match, defaults=dict(
        match_id=match_id
    ))

    team_objects = []
    team_id_relater = dict()
    for i, team in enumerate(teams):
        if team["win"] == "Win":
            win = True
        else:
            win = False

        # Save the relation between list position and the teamId
        # Not assuming that it is always in logical order of 100,200
        team_id_relater.update([str(i),team["teamId"]])

        team_objects[i] = get_or_create(session, models.TeamStats, defaults=dict(
            # Trying to get primary key of Match object we just created
            match_id=match.match_id,
            first_blood=team["firstBlood"],
            first_tower=team["firstTower"],
            first_inhib=team["firstInhib"],
            win=win,
            team_id=team["teamId"]
        ))

    player_objects = []
    for i, participant in enumerate(participants):
        # Check summonerId against database and get or create object
        # Keep objects to have id to link to
        ...



def get_or_create_player(session, player):

    player_object = get_or_create(session, models.Player, defaults=dict(
        account_id=player["accountId"],
        current_account_id=player["accountId"]
    ),
        summoner_id=player["id"])
    return player_object