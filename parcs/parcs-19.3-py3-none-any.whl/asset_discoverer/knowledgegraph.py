def get_assets_list(tenant_id, limit=5):
    assets = [{
        'type': 'Pump',
        'manufacturer': 'Jenbacher',
        'id': 576
    },{
        'type': 'Pump',
        'manufacturer': 'Jenbacher',
        'id': 577
    },{
        'type': 'Pump',
        'manufacturer': 'Jenbacher',
        'id': 578
    },{
        'type': 'Pump',
        'manufacturer': 'Jenbacher',
        'id': 579
    },{
        'type': 'Pump',
        'manufacturer': 'Jenbacher',
        'id': 580
    }
    ]
    return assets

def get_asset_parameters(asset_id, limit=5):
    parameters = [{
        'name': 'Line Volt Unbal',
        'category': 'input',
        'type': 'float',
         'unit': ''%'',
        'parcs_tags': ['performance', 'serviceability']
    },
        {
            'name': 'Power',
            'category': 'input',
            'type': 'float',
            'unit': 'KW',
            'parcs_tags': ['performance', 'serviceability']
        },
        {
            'name': 'Oil Density',
            'category': 'control',
            'type': 'float',
            'unit': 'kg/m3',
            'parcs_tags': ['reliability']
        },
        {
            'name': 'Pmp Inl Prs',
            'category': 'response',
            'type': 'float',
            'unit': 'Bars',
            'parcs_tags': ['performance', 'serviceability', 'reliability']
        },
        {
            'name': 'Pmp Inl Tmp',
            'category': 'input',
            'type': 'float',
            'unit': 'C',
            'parcs_tags': ['performance', 'serviceability', 'reliability']
        }

    ]

    return parameters

def get_asset_components(asset_id):
    components = [{
        'type': 'thrust bearings',
        'manufacturer' : 'Emerson',
        'knowledgegraph_uri': '/765-577/graph',
        'id': '765-577'
    },{
        'type': 'turbines',
        'manufacturer' : 'Jenbacher',
        'knowledgegraph_uri': '/775-577/graph',
        'id': '775-577'
    },{
        'type': 'bottom bearings',
        'manufacturer' : 'Emerson',
        'knowledgegraph_uri': '/775-577/graph',
        'id': '761-577'
    }]

    return components

def get_component_parameters(graph_uri):
    parameters = [{
        'name': 'Vibration',
        'category': 'input',
        'type': 'float',
        'unit': 'g',
        'parcs_tags': ['performance','reliability']
    },
        {
            'name': 'Acoustic',
            'category': 'input',
            'type': 'float',
            'unit': 'Pa . s/m',
            'parcs_tags': ['performance', 'reliability']
        }
    ]

    return parameters
