from unittest import TestCase

from ..example_project.tables import Band, Manager, Concert, Venue


TABLES = [Manager, Band, Venue, Concert]


class TestCreateJoin():

    def test_create_join(self):
        for table in TABLES:
            table.create().run_sync()

        for table in reversed(TABLES):
            table.drop().run_sync()


class TestJoin(TestCase):
    """
    Test instantiating Table instances
    """

    tables = [Manager, Band, Venue, Concert]

    def setUp(self):
        for table in self.tables:
            table.create().run_sync()

    def tearDown(self):
        for table in reversed(self.tables):
            table.drop().run_sync()

    def test_join(self):
        manager_1 = Manager(name="Guido")
        manager_1.save().run_sync()

        band_1 = Band(name="Pythonistas", manager=manager_1.id)
        band_1.save().run_sync()

        manager_2 = Manager(name="Graydon")
        manager_2.save().run_sync()

        band_2 = Band(name="Rustaceans", manager=manager_2.id)
        band_2.save().run_sync()

        venue = Venue(name="Grand Central")
        venue.save().run_sync()

        # TODO - make sure you can also do:
        # band_1=Pythonistas
        save_query = Concert(
            band_1=band_1.id,
            band_2=band_2.id,
            venue=venue.id
        ).save()
        save_query.run_sync()

        select_query = Concert.select().columns(
            Concert.band_1.name,
            Concert.band_2.name,
            Concert.venue.name,
            Concert.band_1.manager
        )
        response = select_query.run_sync()
        print(response)

    # def _test_ref(self):
    #     """
    #     Concert.select().count().where(
    #         Concert.ref('band1.name') == 'Pythonistas'
    #     )
    #     """
    #     pass
