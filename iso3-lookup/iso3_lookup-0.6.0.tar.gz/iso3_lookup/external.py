from iso3_lookup.backend import Lookup

lkp = Lookup()


def get_iso3(country):
    data = [lkp.get_fuzz(v, country, "name") for v in lkp.data]
    mxm, data = lkp.max_data(data)
    return lkp.conf_exists([v for v in data if v["ratio"] == mxm], "alpha-3", country)


def get_country(iso3):
    data = [lkp.get_fuzz(v, iso3, "alpha-3") for v in lkp.data]
    mxm, data = lkp.max_data(data)
    return lkp.conf_exists([v for v in data if v["ratio"] == mxm], "name", iso3)
