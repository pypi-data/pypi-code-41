# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['glutemulo', 'glutemulo.backend', 'glutemulo.kafka']

package_data = \
{'': ['*']}

install_requires = \
['environs>=4.1,<5.0', 'fastavro>=0.21.23,<0.22.0', 'kafka-python>=1.4,<2.0']

extras_require = \
{'carto': ['carto>=1.4,<2.0'],
 'postgres': ['psycopg2-binary>=2.8,<3.0'],
 'redis': ['redis>=3.2,<4.0']}

setup_kwargs = {
    'name': 'geolibs-glutemulo',
    'version': '0.1.2',
    'description': 'GeoLibs data ingestor',
    'long_description': '# Glutemulo\n\nA HA geo socio demo data ingestor\n\n## Usage\n\nRead de [examples files](examples).\n\nWe use environ vars. See [Environ vars file example](.env.example) for complete list,\nand examples.\n\n### Using producer to upload data to kafka\n\nSee python examples bellow. You must produce a dict with column_mame:value\n\n### Using the ingestor consumer\nUse `gluto` docker and fill enviroment vars.\n\nSelect the backend using `GLUTEMULO_BACKEND` and specific vars for it (database, host, etc).\nYou can select 2 backends: `postgres` or `carto`\nSee [Environ vars file example](.env.example) for complete list.\n\nThen set:\n\n1. `GLUTEMULO_INGESTOR_DATASET`  \nTable to upload data\n2. `GLUTEMULO_INGESTOR_DATASET_COLUMNS`  \nComma separted list of column names\n\nNow, create the table on backend or set `GLUTEMULO_INGESTOR_DATASET_DDL` and `GLUTEMULO_INGESTOR_DATASET_AUTOCREATE=False`\n\nThen configure ingestor for kafka.\nFirst read the [python-kafka doc](https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html)\nand then use the following vars:\n\n1. `GLUTEMULO_INGESTOR_TOPIC`  \nTopic to use\n2. `GLUTEMULO_INGESTOR_BOOTSTRAP_SERVERS`  \nList of servers to connect\n3. `GLUTEMULO_INGESTOR_GROUP_ID`  \nGroup id.\n4. `GLUTEMULO_INGESTOR_AUTO_OFFSET_RESET`  \nlatest or earliest.\n5. `GLUTEMULO_INGESTOR_MAX_POLL_RECORDS`  \nThe maximum number of records returned in a batch of messages\n6. `GLUTEMULO_INGESTOR_FETCH_MIN_BYTES`  \nMinimum amount of data the server should return for a fetch request, otherwise wait up to fetch_max_wait_ms for more data to accumulate. Default: 1\n\nFor the docker, we include a [example docker-compose file](docker-compose.yml).\nRemember you can scale with same group_id\n\n```bash\ndocker-compose scale gluto=3\n```\n\n## Run flask demo\n\n```bash\n$ FLASK_ENV=development flask run\n * Environment: development\n * Debug mode: on\n * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)\n * Restarting with stat\n * Debugger is active!\n * Debugger PIN: 194-409-049\n```\n\n## Test\n\n```bash\n$ http -j POST localhost:5000/v1/ uno=1 dos=2`\nHTTP/1.0 201 CREATED\nContent-Length: 13\nContent-Type: text/html; charset=utf-8\nDate: Thu, 02 May 2019 14:56:07 GMT\nServer: Werkzeug/0.15.2 Python/3.7.2\n\nDATA Received\n```\n\n## Producer / Consumer\n\n### Kafka + json\n\nAsync producer:\n\n```python\nfrom glutemulo.kafka.producer import JsonKafka\nproductor = JsonKafka(bootstrap_servers="localhost:9092")\nfuture = productor.produce(\'simple-topic\', dict(dos=\'BB\'))\n```\n\nConsumer in batches:\n```python\nfrom glutemulo.kafka.consumer import JsonKafka\nconsumer = JsonKafka(\'simple-topic\', bootstrap_servers="localhost:9092")\nfor msg in consumer.consume():\n    for msg in messages:\n        print(msg)\n```\n\n### Kafka + Avro\n\nsync producer:\n\n```python\nSCHEMA = {\n    "type": "record",\n    "name": "simpledata",\n    "doc": "This is a sample Avro schema to get you started.",\n    "fields": [\n        {"name": "name", "type": "string"},\n        {"name": "number1", "type": "int"},\n    ],\n}\nSCHEMA_ID = 1\n```\n\n```python\nfrom glutemulo.kafka.producer import AvroKafka as Producer\nproductor = Producer(SCHEMA, SCHEMA_ID,bootstrap_servers="localhost:9092")\nfuture = productor.produce(\'simple-topic-avro\', dict(name=\'Un nombre\', number1=10))\n```\n\nConsumer:\n```python\nfrom glutemulo.kafka.consumer import AvroKafka as Consumer\nconsumer = Consumer(\'simple-topic-avro\', SCHEMA, SCHEMA_ID, bootstrap_servers="localhost:9092")\nfor messages in consumer.consume():\n    for msg in messages:\n        print(msg)\n```\n\n## For testing\n\nYou can setup a Kafka Consumer using the kafka-console-consumer script that comes with Kafka.\n\n```bash\n$ bin/kafka-console-consumer.sh --bootstrap-server 192.168.1.240:9092 --topic pylog --from-beginning\n\nthis is an awsome log\n```\n\n### Testing With KafkaCat\n\nYou ca use an application called KafkaCat.\n\nAfter the application is installed we will run it in consumer mode (which is the default).\n\n```bash\nkafkacat -b 192.168.240.41:9092 -t one-test\n```\n\nThis should not show anything yet because we haven\'t sent anything to our topic yet...\n\nTo send stuff we can copy any text file into our current directory and send it to our Kafka Topic. In another window, run the following command.\n\n```bash\n$ cat README | kafkacat -b 192.168.240.41 -t one-test\n```\nYou should see the output in the first window which has KafkaCat still running in consumer mode.\n\n\n## Links\n\n- [Zoonavigator](http://localhost:8004). Use \'zoo1\' as connection string\n- [schema-registry-ui](http://localhost:8001)\n- [Rebrow](http://localhost:5001)\n- [kafka topics ui](http://localhost:8000)\n- [kafka rest proxy](http://localhost:8082)\n',
    'author': 'Geographica',
    'author_email': 'hello@geographica.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
