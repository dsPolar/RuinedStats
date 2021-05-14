from riotwatcher import LolWatcher, ApiError
import pandas as pd
import numpy as np

from api_key import key
import aram_single_summoner
from data_dragon_handler import create_champion_id_dict

def get_data_for_match(teams, participants):

    return_data = {"blueTeam" : None, "redTeam" : None}
    blue_team = {"championIds" : [], "win" : None, "ranks" : [], "spells" : [],
                 "firstBlood" : None, "firstTower" : None, "firstInhib" : None}
    # Create a copy dictionary, copies each internal reference rather than just new reference to same object
    # This way they can be changed independently, unlike using =
    red_team = blue_team.copy()


    for team in teams:
        if team["teamId"] == 100:
            if team["firstBlood"]:
                blue_team["firstBlood"] = True
                red_team["firstBlood"] = False
            else
                blue_team["firstBlood"] = False
                red_team["firstBlood"] = True

            if team["firstTower"]:
                blue_team["firstTower"] = True
                red_team["firstTower"] = False
            else
                blue_team["firstTower"] = False
                red_team["firstTower"] = True

            if team["firstInhibitor"]:
                blue_team["firstInhib"] = True
                red_team["firstInhib"] = False
            else
                blue_team["firstInhib"] = False
                red_team["firstInhib"] = True

            # Potential fraction of games that end as a result of server crash
            # or maintenance, would result in both teams losing potentially
            # Going to assume this fraction is too small to care about given that
            # I've never had one in 2500 games
            if team["win"] == "Win":
                blue_team["win"] = True
                red_team["win"] = False
            else
                blue_team["win"] = False
                red_team["win"] = True

    for player in participants:
