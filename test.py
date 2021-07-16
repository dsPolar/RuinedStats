from typing import Any, Tuple

from ruined_stats import models, persister, cli
import unittest


class TestRowCreation(unittest.TestCase):
    session = models.get_testing_database_session()

    def test_add_player(self):
        player = {"id": "jiE6NGM_ddgkCi93q2gzhxT6X5ZooJkpN97TmQ7jLkERboQ",
                  "accountId": "Y8ahNI3O8mMC_LNYrYykVUG_qbZHm0P18Q5Nq6Nzuv2giA",
                  "puuid": "lKTUv_R_ocQqnGOj87fV4XKJjpUjfn0A54CETr-bkFjEUVKuVSOJaX6dPoIrMNEd5Ku3NmmShuQsKQ"}

        player_object = persister.get_or_create_player(self.session, player)
        self.assertTrue(self.session.query(models.Player).filter_by(account_id=player["accountId"]).first() is not None)

    def test_add_player_object(self):
        player = models.Player(summoner_id="jiE6NGM_ddgkCi93q2gzhxT6X5ZooJkpN97TmQ7jLkERboQ",
                               account_id="Y8ahNI3O8mMC_LNYrYykVUG_qbZHm0P18Q5Nq6Nzuv2giA",
                               puuid="lKTUv_R_ocQqnGOj87fV4XKJjpUjfn0A54CETr-bkFjEUVKuVSOJaX6dPoIrMNEd5Ku3NmmShuQsKQ",
                               scraped=False)

        player_object = persister.get_or_create_with_object(self.session, models.Player, player,
                                                            account_id=player.account_id)
        self.assertTrue(self.session.query(models.Player).filter_by(account_id=player.account_id).first() is not None)

    def test_add_match(self):
        riot_match_id = "55555555555"
        match_object = persister.get_or_create(self.session, models.Match, defaults=dict(), riot_match_id=riot_match_id)
        self.assertTrue(self.session.query(models.Match).filter_by(riot_match_id=riot_match_id).first() is not None)

    def test_add_team_stats(self):
        riot_match_id = "6666666666"
        match_object: Tuple[Any, bool] = persister.get_or_create(self.session, models.Match, defaults=dict(), riot_match_id=riot_match_id)
        team_stats_object = persister.get_or_create(self.session, models.TeamStats, defaults=dict(
            first_blood=True,
            first_tower=True,
            first_inhib=True,
            win=True,
            team_id="100"
        ),
                                                    match_id=match_object[0].match_id)
        self.assertTrue(self.session.query(models.TeamStats).filter_by(match_id=match_object[0].match_id, team_id="100").first() is not None)

    def test_set_player_scraped(self):
        player = models.Player(summoner_id="jiE6NGM_ddgkCi93q2gzhxT6X5ZooJkpN97TmQ7jLkERboQa",
                               account_id="Y8ahNI3O8mMC_LNYrYykVUG_qbZHm0P18Q5Nq6Nzuv2giAa",
                               puuid="lKTUv_R_ocQqnGOj87fV4XKJjpUjfn0A54CETr-bkFjEUVKuVSOJaX6dPoIrMNEd5Ku3NmmShuQsKQa",
                               scraped=False)

        player_object = persister.get_or_create_with_object(self.session, models.Player, player,
                                                            account_id=player.account_id)
        persister.update_player_scraped(self.session, player_object[0], True)
        self.assertTrue(self.session.query(models.Player).filter_by(account_id=player.account_id).first().scraped)

    def test_set_player_scraped_get_unscraped(self):
        player = models.Player(summoner_id="jiE6NGM_ddgkCi93q2gzhxT6X5ZooJkpN97TmQ7jLkERboQab",
                               account_id="Y8ahNI3O8mMC_LNYrYykVUG_qbZHm0P18Q5Nq6Nzuv2giAab",
                               puuid="lKTUv_R_ocQqnGOj87fV4XKJjpUjfn0A54CETr-bkFjEUVKuVSOJaX6dPoIrMNEd5Ku3NmmShuQsKQab",
                               scraped=False)
        new_player = models.get_unscraped_player()
        persister.update_player_scraped(self.session, new_player, True)
        self.assertFalse(new_player.account_id != models.get_unscraped_player().account_id)

        
if __name__ == "__main__":
    unittest.main()
