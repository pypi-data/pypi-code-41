from .ZeitzonoDB import ZeitzonoDB
from .ZeitzonoCities import ZeitzonoCities
from .ZeitzonoCity import ZeitzonoCity


class ZeitzonoSearch:
    """
    will search for city names
    returns Cities object with number of results found

    """

    def __init__(self):
        self.hdb = ZeitzonoDB()

    def _format_db_results(self, results, numresults):

        cities = []
        for result in results:
            name = result[0]
            country = result[1]
            admin1 = result[2] or ""  # needed to convert None to empty string
            admin2 = result[3] or ""  # needed to convert None to empty string
            tz = result[4]
            city = ZeitzonoCity(name, country, admin1, admin2, tz)
            cities.append(city)

        return ZeitzonoCities(cities=cities, nresults=numresults)

    def search(self, term1=None, term2=None, subterm=None, limitamt=25):
        term1_l = term1.lower() if term1 is not None else None
        term2_l = term2.lower() if term2 is not None else None
        subterm_l = subterm.lower() if subterm is not None else None

        if (term1 is None) or (len(term1.strip()) == 0):
            return ZeitzonoCities(nresults=0)

        numresults = self.hdb.db_count(term1_l, term2_l, subterm_l)

        if numresults <= 0:
            return ZeitzonoCities(nresults=0)

        limit = False
        if numresults > limitamt:
            limit = True

        results = self.hdb.db_search(
            term1_l, term2_l, subterm_l, limit=limit, limitamt=limitamt
        )

        return self._format_db_results(results, numresults)

    def random1(self):
        results = self.hdb.random_cities(1)
        return self._format_db_results(results, None)

    def random10(self):
        results = self.hdb.random_cities(10)
        return self._format_db_results(results, None)
