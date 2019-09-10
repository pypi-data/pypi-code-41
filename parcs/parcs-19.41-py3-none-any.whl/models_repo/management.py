def get_parcs_models(asset_id):
    models = [{
        'model_category': 'performance',
        'model_source_code_repository': 'https://gitlab.qiotec-internal.com/data-science/jenbacher-performance',
        'model_instance_in_production': 'http://modelmanagement.fe-dev.qiodev.qiotec-internal.com/#/experiments/3/runs/db9d4c4c447b49c9b94c094d675758bf',
        'model_instance_in_staging':'http://modelmanagement.fe-dev.qiodev.qiotec-internal.com/#/experiments/3/runs/3cb52dbbfa54469887d3187a59b59e06'
    },{
        'model_category': 'availability',
        'model_source_code_repository': 'https://gitlab.qiotec-internal.com/data-science/jenbacher-availability',
        'model_instance_in_production': 'http://modelmanagement.fe-dev.qiodev.qiotec-internal.com/#/experiments/17/runs/619df9c76bf5490e830d045c01719376',
        'model_instance_in_staging':''
    },{
        'model_category': 'reliability',
        'model_source_code_repository': 'https://gitlab.qiotec-internal.com/data-science/jenbacher-reliability',
        'model_instance_in_production': 'http://modelmanagement.fe-dev.qiodev.qiotec-internal.com/#/experiments/3/runs/db9d4c4c447b49c9b94c094d675758bf',
        'model_instance_in_staging':'http://modelmanagement.fe-dev.qiodev.qiotec-internal.com/#/experiments/3/runs/3cb52dbbfa54469887d3187a59b59e06'
    },{
        'model_category': 'capacity',
        'model_source_code_repository': 'https://gitlab.qiotec-internal.com/data-science/jenbacher-capacity',
        'model_instance_in_production': 'http://modelmanagement.fe-dev.qiodev.qiotec-internal.com/#/experiments/24/runs/5fc88abf42c44bd18e5fab55a1c18b80',
        'model_instance_in_staging':''
    },{
        'model_category': 'serviceability',
        'model_source_code_repository': 'https://gitlab.qiotec-internal.com/data-science/jenbacher-serviceability',
        'model_instance_in_production': 'http://modelmanagement.fe-dev.qiodev.qiotec-internal.com/#/experiments/31/runs/482be4015a104742ac475dba23fcfd9b',
        'model_instance_in_staging':''
    }]

    return models