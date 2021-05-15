from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
import pathlib
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TeamID(enum.Enum):
    BLUE = "100"
    RED = "200"


class Player(Base):
    __tablename__ = 'player'

    player_id = Column(Integer, primary_key=True)

    account_id = Column(String, unique=True)
    current_account_id = Column(String, unique=True)
    summoner_id = Column(String, unique=True)

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

    team_id = Column(EnumField(TeamID))


class Match(Base):
    __tablename__ = 'match'
    match_id = Column(Integer, primary_key=True)
    riot_match_id = Column(String, unique=True)

    teams = relationship("TeamStats")




engine = create_engine('sqlite:///ruined_stats.db')
