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


def create_match(session, match, teams, players):
    ...


def create_player(session, player):

    get_or_create(session, models.Player, defaults=dict(
        account_id=player["accountId"],
        current_account_id=player["accountId"]
    ),
        summoner_id=player["id"])
