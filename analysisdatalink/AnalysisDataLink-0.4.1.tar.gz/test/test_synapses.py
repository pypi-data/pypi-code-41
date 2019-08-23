from connectomeanalysis import ConnectomeAnalysis
def test_connectome():
    postgres_uri = "postgresql://postgres:welcometothematrix@35.196.105.34/postgres"
    connectome = ConnectomeAnalysis(postgres_uri = postgres_uri)
    object_ids = connectome.get_object_ids()
    synapses = connectome.get_synapses_from_object_ids(object_ids[0])

import connectomeanalysis
def test_connectome():
    postgres_uri = "postgresql://postgres:welcometothematrix@35.196.105.34/postgres"
    connectome = connectomeanalysis.ConnectomeConnect(postgres_uri= postgres_uri)
    object_ids = connectomeanalysis.objects.get_object_ids(connectome=connectome)
    synapses = connetomeanalysis.synapses.get_synapses_from_object_ids(object_id = object_ids[0],
                                                                       connectome=connectome)

