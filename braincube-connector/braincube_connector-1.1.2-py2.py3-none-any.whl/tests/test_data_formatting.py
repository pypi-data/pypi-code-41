from braincube.bc_connector.data_formatting import data_to_dataframe, get_data_with_id

fakeRef = {'referenceDate': 'mb888/d99999992',
           'timezone': 'Etc/GMT',
           'hfUrl': 'http://TESTING:9999/MX_FAKE',
           'datadefs': [{'type': 'NUMERIC', 'id': 'mb888/d99999991'},
                        {'type': 'DATETIME', 'id': 'mb888/d99999992'},
                        {'type': 'DATETIME', 'id': 'mb888/d99999993'},
                        {'type': 'DISCRET', 'id': 'mb888/d99999994'},
                        {'type': 'NUMERIC', 'id': 'mb888/d99999995'},
                        {'type': 'DISCRET', 'id': 'mb888/d99999996'},
                        {'type': 'DISCRET', 'id': 'mb888/d99999997'},
                        {'type': 'NUMERIC', 'id': 'mb888/d99999998'},
                        {'type': 'NUMERIC', 'id': 'mb888/d99999999'}],
           'reference': 'mb888/d99999991',
           'order': 'mb888/d99999992',
           'name': 'mb888',
           'lfUrl': 'http://TESTING:9999/MX_FAKE'}

fakeData = [{'type': 'DATETIME',
             'id': 'mb888/d99999992',
             'data': ['20120102_000000', '20120103_000000', '20120103_000000']},
            {'type': 'NUMERIC',
             'id': 'mb888/d99999998',
             'data': ['377.4', '376.4', '376.4']},
            {'type': 'DISCRET',
             'id': 'mb888/d99999994',
             'data': ['IMMÉDIAT', 'NORMAL', 'URGENT']}
            ]

fakeDataDef = [{'bcId': 99999999, 'local': 'Age du Ticlet en mois', 'tag': 'Age du Ticlet en mois', 'id': 99999999,
                'standard': 'Age du Ticlet en mois'},
               {'bcId': 99999998, 'local': 'Age du ticket', 'tag': 'Age du ticket', 'id': 99999998,
                'standard': 'Age du ticket'},
               {'bcId': 99999997, 'local': 'Tracker', 'tag': 'Tracker', 'id': 99999997, 'standard': 'Tracker'},
               {'bcId': 99999992, 'local': 'created', 'tag': 'created', 'id': 99999992, 'standard': 'created'},
               {'bcId': 99999995, 'local': 'duration', 'tag': 'duration', 'id': 99999995, 'standard': 'duration'},
               {'bcId': 99999991, 'local': 'N° de Ticket', 'tag': 'issue', 'id': 99999991, 'standard': 'N° de Ticket'},
               {'bcId': 99999994, 'local': 'priority', 'tag': 'priority', 'id': 99999994, 'standard': 'priority'},
               {'bcId': 99999993, 'local': 'solved', 'tag': 'solved', 'id': 99999993, 'standard': 'solved'},
               {'bcId': 99999996, 'local': 'status', 'tag': 'status', 'id': 99999996, 'standard': 'status'}]


def test_map_data():
    tt = get_data_with_id(fakeData)
    assert tt.get('99999992')[2] == "20120103_000000"
    assert tt.get('99999994')[2] == "URGENT"
    assert tt.get('99999998')[2] == "376.4"


def test_data_formating():
    test = data_to_dataframe(fakeData, fakeDataDef, fakeRef)
    assert test.columns[0] == "Age du ticket"
    assert test.columns[1] == "priority"
    assert test.values[0][0] == "377.4"
    assert test.values[0][1] == "IMMÉDIAT"
