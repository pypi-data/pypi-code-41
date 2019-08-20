from ..base import DBTestCase
from ..example_project.tables import Band


class TestExists(DBTestCase):

    def test_exists(self):
        self.insert_rows()

        response = Band.count().where(
            Band.name == 'Pythonistas'
        ).run_sync()

        self.assertTrue(response == True)
