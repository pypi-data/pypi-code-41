import logging
import os

from polytropos.ontology.task import Task
from polytropos.actions import register_all

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

register_all()

#data: str = os.path.join("/Users/dbborens/dmz/github/analysis/etl5/output")
#conf = os.path.join("/Users/dbborens/dmz/github/analysis/etl5")
#task = Task.build(conf, data, "clients/dinnouti/main")
data: str = os.path.join("/tmp/etl5_fixture_tests")
conf = os.path.join("/Users/dbborens/dmz/github/analysis/etl5")
task = Task.build(conf, data, "origin_to_logical_tr_only")
task.run()
