import logging
import os

from polytropos.ontology.task import Task

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

data: str = os.path.join("/tmp/debug")
conf = os.path.join("/Users/dbborens/dmz/github/analysis/etl5")
task = Task.build(conf, data, "origin_to_logical_tr_only")
task.run()
