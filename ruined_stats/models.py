import enum

from sqlalchemy import create_engine, ForeignKey, Enum, Boolean
from sqlalchemy import Column, Integer, String

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()


class TeamID(enum.Enum):
    BLUE = "100"
    RED = "200"

class Player(Base):
    __tablename__ = 'player'

    player_id = Column(Integer, primary_key=True)

    summoner_id = Column(String)
    account_id = Column(String, unique=True)
    puuid = Column(String, unique=True)
    scraped = Column(Boolean, default=False)

    participants = relationship("Participant")


class Participant(Base):
    __tablename__ = 'participant'
    participant_id = Column(Integer, primary_key=True)

    player_id = Column(Integer, ForeignKey("player.player_id"))

    team_participant_id = Column(Integer)
    champion_id = Column(Integer)

    team_stats_id = Column(Integer, ForeignKey("teamstats.team_stats_id"))


class TeamStats(Base):
    __tablename__ = 'teamstats'
    team_stats_id = Column(Integer, primary_key=True)

    match_id = Column(Integer, ForeignKey("match.match_id"))

    first_blood = Column(Boolean)
    first_tower = Column(Boolean)
    first_inhib = Column(Boolean)

    win = Column(Boolean)

    team_id = Column(String)


class Match(Base):
    __tablename__ = 'match'
    match_id = Column(Integer, primary_key=True)
    riot_match_id = Column(String, unique=True)

    teams = relationship("TeamStats")


def get_unscraped_player():
    session = Session()
    sql_player = session.query(Player).filter(Player.scraped == False).first()

    if sql_player:
        return sql_player
    else:
        return None

def get_unscraped_player_not_listed(blacklist):
    session = Session()
    sql_player = session.query(Player).filter(Player.scraped == False, ~Player.account_id.in_((item.account_id for item in blacklist))).first()
    return sql_player


def get_testing_database_session():
    test_engine = create_engine('sqlite:///test_stats.db')
    Base.metadata.create_all(test_engine)
    Session = sessionmaker(bind=test_engine)
    session = Session()
    return session

def testing_tear_down(test_engine):
    Base.metadata.drop_all(test_engine)


engine = create_engine('sqlite:///ruined_stats.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
