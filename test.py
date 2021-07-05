from ruined_stats import models, persister, cli
import unittest


class TestRowCreation(unittest.TestCase):
    session = models.get_testing_database_session()

    def test_add_player(self):
        player = {"id": "jiE6NGM_ddgkCi93q2gzhxT6X5ZooJkpN97TmQ7jLkERboQ",
                  "accountId": "Y8ahNI3O8mMC_LNYrYykVUG_qbZHm0P18Q5Nq6Nzuv2giA",
                  "puuid": "lKTUv_R_ocQqnGOj87fV4XKJjpUjfn0A54CETr-bkFjEUVKuVSOJaX6dPoIrMNEd5Ku3NmmShuQsKQ"}

        player_object = persister.get_or_create_player(self.session, player)
        self.assertIn(player_object, self.session.query(models.Player))

    def test_add_match(self):
        riot_match_id = "55555555555"
        match_object = persister.get_or_create(self.session, models.Match, defaults=dict(), riot_match_id=riot_match_id)
        self.assertIn(match_object, self.session.query(models.Match))

    def test_add_team_stats(self):
        riot_match_id = "6666666666"
        match_object = persister.get_or_create(self.session, models.Match, defaults=dict(), riot_match_id=riot_match_id)
        team_stats_object = persister.get_or_create(self.session, models.TeamStats, defaults=dict(
            first_blood=True,
            first_tower=True,
            first_inhib=True,
            win=True,
            team_id="100"
        ),
                                                    match_id=match_object.match_id)
        self.assertIn(team_stats_object, self.session.query(models.TeamStats))
