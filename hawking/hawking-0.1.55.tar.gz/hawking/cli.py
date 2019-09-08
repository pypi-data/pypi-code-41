""" Hawking CLI.

Hawking Search Engine Command Line Interface (CLI).
Copyright (C) 2019 Peach Inc. All rights reserved.
"""
import os
import click
import json
import shutil
import subprocess
import time

import grpc

from hawking.common.color import *


_HAWKING_BASE_IMAGE = 'hawking-base:0.1'
_BASE_PIP_PACKAGES = 'hawking==0.1.52 hawking_proto==0.1.15 faiss-cpu'


def bold(skk):
    print_color(skk, bold=True, color=LIGHT_YELLOW)


def info(skk):
    print_color(skk, color=LIGHT_CYAN)


def hilite(skk):
    print_color(skk, underline=True, color=LIGHT_GREEN)


def shell_execute(cmds):
    for cmd in cmds:
        info("executing: `{}`".format(cmd))
        os.system(cmd)


def get_container_ip(tag):
    cmd = "docker ps | awk '{ if ($2 == \"%s\") { print $1 }}' | xargs docker container inspect" % (tag)
    result = subprocess.check_output(cmd, shell=True)
    r = json.loads(result)
    ip_addresses = []
    for i in r:
        ip = i['NetworkSettings']['IPAddress']
        ip_addresses.append(ip)
        print(ip)
    return ip_addresses


def kill_container(tag):
    cmd = "docker ps | awk '{ if ($2 == \"%s\") { print $1 } }' | xargs docker kill" % (tag)
    result = subprocess.check_output(cmd, shell=True)
    print(result.decode('utf-8'))


@click.group()
def cli():
    pass


def build_base_image(dockerfile='hawking.dockerfile.tmp'):
    def create_docker_file(p_dockerfile):
        with open(p_dockerfile, 'w') as f:
            f.write("""
FROM hawking-rte:0.1

# Separating this as an optimization, since pytorch is a large .whl (768mb)
RUN apt-get update \
    && . /root/miniconda3/etc/profile.d/conda.sh \
    && conda activate hawking \
    && pip install torch pytorch-transformers

RUN . /root/miniconda3/etc/profile.d/conda.sh \
    && conda activate hawking \
    && pip install {0}
""".format(_BASE_PIP_PACKAGES))

    create_docker_file(dockerfile)
    cmds = [
        'docker build -f {} -t {} .'.format(dockerfile, _HAWKING_BASE_IMAGE),
        'cat {0}'.format(dockerfile),
        'rm -f {0}'.format(dockerfile),
    ]
    shell_execute(cmds)


def deploy_bot_as_local_docker_daemon(token, dockerfile, tag, build_only=False):
    def create_docker_file(p_dockerfile):
        with open(p_dockerfile, 'w') as f:
            f.write("""
FROM {0}

CMD . /root/miniconda3/etc/profile.d/conda.sh \
  && conda activate hawking \
  && hawking start bot > /tmp/bot.log 2> /tmp/bot.err
""".format(_HAWKING_BASE_IMAGE))
    create_docker_file(dockerfile)

    cmds = [
        'docker build -f {} -t {} .'.format(dockerfile, tag),
        'docker run -d --rm -v /tmp:/tmp -e BOT_TOKEN="{0}" {1}'.format(token, tag),
        'cat {0}'.format(dockerfile),
        'rm -f {0}'.format(dockerfile),
    ]

    shell_execute([cmds[0], cmds[2], cmds[3]] if build_only else cmds)


def deploy_secretary_as_local_docker_daemon(token, dockerfile, tag, build_only=False):
    def create_docker_file(p_dockerfile):
        with open(p_dockerfile, 'w') as f:
            f.write("""
FROM {0}

CMD . /root/miniconda3/etc/profile.d/conda.sh \
  && conda activate hawking \
  && hawking start secretary > /tmp/secretary.log 2> /tmp/secretary.err
""".format(_HAWKING_BASE_IMAGE))
    create_docker_file(dockerfile)

    cmds = [
        'docker build -f {} -t {} .'.format(dockerfile, tag),
        'docker run -d --rm -v /tmp:/tmp -e BOT_TOKEN="{0}" {1}'.format(token, tag),
        'cat {0}'.format(dockerfile),
        'rm -f {0}'.format(dockerfile),
    ]

    shell_execute([cmds[0], cmds[2], cmds[3]] if build_only else cmds)


def deploy_caption_serving_as_local_docker_daemon(data_root, args, dockerfile, tag, port, build_only=False):
    def create_docker_file(p_dockerfile):
        with open(p_dockerfile, 'w') as f:
            f.write("""
FROM {0}

CMD . /root/miniconda3/etc/profile.d/conda.sh \
  && conda activate hawking \
  && hawking start caption $ARGS > /tmp/caption.log 2> /tmp/caption.err
""".format(_HAWKING_BASE_IMAGE))
    create_docker_file(dockerfile)
    cmds = [
        'docker build -f {} -t {} .'.format(dockerfile, tag),
        'docker run -d --rm -p {0}:{0} -v {1}:/data/ -v /tmp:/tmp -v $PWD:/host -e ARGS="{2}" {3}'.format(
            port, data_root, args, tag),
        'cat {0}'.format(dockerfile),
        'rm -f {0}'.format(dockerfile),
    ]
    shell_execute([cmds[0], cmds[2], cmds[3]] if build_only else cmds)


def deploy_fx_serving_as_local_docker_daemon(data_dir, args, dockerfile, tag, port, build_only=False):
    def create_docker_file(p_dockerfile):
        with open(p_dockerfile, 'w') as f:
            f.write("""
FROM {0}

CMD . /root/miniconda3/etc/profile.d/conda.sh \
  && conda activate hawking \
  && hawking start fx $ARGS > /tmp/fx.log 2> /tmp/fx.err
""".format(_HAWKING_BASE_IMAGE))
    create_docker_file(dockerfile)

    cmds = [
        'docker build -f {} -t {} .'.format(dockerfile, tag),
        'docker run -d --rm -p {0}:{0} -v {1}:/data/ -v /tmp:/tmp -v $PWD:/host -e ARGS="{2}" {3}'.format(
            port, data_dir, args, tag),
        'cat {0}'.format(dockerfile),
        'rm -f {0}'.format(dockerfile),
    ]

    shell_execute([cmds[0], cmds[2], cmds[3]] if build_only else cmds)


def deploy_sx_serving_as_local_docker_daemon(index_dir, index_name, args, dockerfile, port, tag, build_only=False):
    def create_docker_file(p_dockerfile):
        with open(p_dockerfile, 'w') as f:
            f.write("""
FROM {0}

RUN mkdir -p /app/sptag

COPY $HAWKING_ROOT/src/cli/hawking/serve/sptag_server.py /app/sptag

WORKDIR /app/sptag

CMD . /root/miniconda3/etc/profile.d/conda.sh \
  && conda activate hawking \
  && /bin/bash -c "python /app/sptag/sptag_server.py --index-path /data/$INDEX_NAME $ARGS"
""".format(_HAWKING_BASE_IMAGE))

    create_docker_file(dockerfile)

    cmds = [
        'docker build -f {} -t {} .'.format(dockerfile, tag),
        'docker run -d --rm -p {0}:{0} -v {1}:/data/ -e INDEX_NAME="{2}" -e ARGS="{3}" {4}'.format(
            port, index_dir, index_name, args, tag),
        'cat {0}'.format(dockerfile),
        'rm -f {0}'.format(dockerfile),
    ]

    shell_execute([cmds[0], cmds[2], cmds[3]] if build_only else cmds)


def deploy_bert_serving_as_local_docker_daemon(model_dir, model_name, args, dockerfile, tag, build_only=False):
    def create_docker_file(p_dockerfile):
        with open(p_dockerfile, 'w') as f:
            f.write("""
FROM {0}

CMD . /root/miniconda3/etc/profile.d/conda.sh \
  && conda activate hawking \
  && echo BERT_ARGS=$BERT_ARGS \
  && /bin/bash -c "$(which bert-serving-start) -model_dir=/data/{1} $BERT_ARGS"
""".format(_HAWKING_BASE_IMAGE, model_name))

    create_docker_file(dockerfile)

    cmds = [
        'docker build -f {} -t {} .'.format(dockerfile, tag),
        'docker run -d -p 5555:5555 -p 5556:5556 -v {0}:/data/ -e BERT_ARGS="{1}" {2}'.format(model_dir, args, tag),
        'cat {0}'.format(dockerfile),
        'rm -f {0}'.format(dockerfile),
    ]

    shell_execute([cmds[0], cmds[2], cmds[3]] if build_only else cmds)


def deploy_sx_indexer_as_local_docker_daemon(index_dir, index_name, service_ini, dockerfile, port, tag, build_only=False):
    """ Deploy SX backend server local docker. """
    def create_service_ini(p_output, p_index_name, p_port, p_max_result_count=5):
        """ Do a set of regexes to replace default values with overrides. """
        service_ini_tmpl = "$HAWKING_ROOT/src/cli/hawking/sptag/service.ini"
        _cmds = [
            ("sed -e 's/ListenPort=.*/ListenPort={0}/g' {1}".format(p_port, service_ini_tmpl)),
            ("sed -e 's/DefaultMaxResultNumber=.*/DefaultMaxResultNumber={0}/g'".format(p_max_result_count)),
            ("sed -e 's/merge_2006-10_2007-04-08_2018-05/{0}/g'".format(p_index_name))
        ]

        os.system("cp {0} {1}".format(service_ini_tmpl, p_output))
        _cmd_string = _cmds[0]
        for _cmd in _cmds[1:]:
            _cmd_string += " | " + _cmd
        _cmd_string += " > " + p_output
        print(_cmd_string)
        os.system(_cmd_string)

    def create_docker_file(p_dockerfile, p_service_ini, p_index_dir, p_index_name):
        with open(p_dockerfile, 'w') as f:
            f.write("""
FROM hawking-rte:0.1
COPY $HAWKING_ROOT/src/cli/hawking/sptag/server /app/sptag/
COPY {2} /app/sptag/service.ini
ENTRYPOINT ["/bin/bash", "-c", "/app/sptag/server -m socket -c /app/sptag/service.ini"]
""".format(p_index_dir, p_index_name, p_service_ini))

    hawking_root = os.environ.get('HAWKING_ROOT')
    if hawking_root is None:
        assert False, "$HAWKING_ROOT is not set. Aborting ..."
    assert os.path.exists("{0}/src/cli/hawking/sptag".format(hawking_root)), \
        "`{0}/src/cli/hawking/sptag` does not exist. Aborting ...".format(hawking_root)
    assert os.path.exists("{0}/{1}".format(index_dir, index_name)), \
        "Index `{0}/{1}` does not exist. Aborting ...".format(index_dir, index_name)
    create_service_ini(service_ini, index_name, port)
    create_docker_file(dockerfile, service_ini, index_dir, index_name)

    cmds = [
        'docker build -f {0} -t {1} .'.format(dockerfile, tag),
        'docker run -d -p {0}:{0} -v {1}:/data {2}'.format(port, index_dir, tag),
        'cat {}'.format(dockerfile),
        'rm -f {0} && rm -f {1}'.format(dockerfile, service_ini)
    ]

    shell_execute([cmds[0], cmds[2], cmds[3]] if build_only else cmds)


def deploy_queue_as_local_docker_daemon(queue_dir, args, dockerfile, port, tag, build_only=False):
    # TODO(oleg): refactor similar to fx and caption
    def create_docker_file(p_dockerfile):
        with open(p_dockerfile, 'w') as f:
            f.write("""
FROM {0}

RUN mkdir -p /app/queue

COPY $HAWKING_ROOT/src/cli/hawking/serve/queue_server.py /app/queue

WORKDIR /app/queue

CMD . /root/miniconda3/etc/profile.d/conda.sh \
  && conda activate hawking \
  && /bin/bash -c "python /app/queue/queue_server.py --queue-path /data $ARGS"
""".format(_HAWKING_BASE_IMAGE))
    create_docker_file(dockerfile)

    cmds = [
        'docker build -f {} -t {} .'.format(dockerfile, tag),
        'docker run -d -p {0}:{0} -v {1}:/data/ -e ARGS="{2}" {3}'.format(
            port, queue_dir, args, tag),
        'cat {0}'.format(dockerfile),
        'rm -f {0}'.format(dockerfile),
    ]

    shell_execute([cmds[0], cmds[2], cmds[3]] if build_only else cmds)


@cli.group()
def deploy():
    """ Deploy command group. """
    build_base_image()
    pass


@deploy.command()
@click.argument('data_root')
@click.argument('index_name')
@click.option('--grpc-port', help='Server port.', default=50001)
@click.option('--tag', '-t', help='Frontend container tag.', default='caption-serving:0.1')
@click.option('--worker-threads', '-w', help='Max worker threads.', default=10)
@click.option('--build-only/--no-build-only', help='Build docker image only.', default=False)
def caption(data_root, index_name, grpc_port, tag, worker_threads, build_only):
    """ Deploy Caption serving node. """
    print('[Deploy Caption index serving node]')
    assert os.path.exists(data_root), "data_root: {} does not exist.".format(data_root)
    index_path = os.path.join(data_root, index_name)
    if not index_path.endswith('.caption'):
        index_path = '{}.caption'.format(index_path)
    assert os.path.exists(index_path), "--index-path `{}` does not exist. Aborting.".format(index_path)
    args = '--index-path /data/{} --worker-threads {} --grpc-port {}'.format(index_name, worker_threads, grpc_port)
    deploy_caption_serving_as_local_docker_daemon(data_root, args, 'caption-serving.dockerfile.tmp', tag, grpc_port,
                                                  build_only=build_only)


@deploy.command()
@click.option('--token', help='BOT_TOKEN value.', default='701884073:AAF9rkmy73sq6U3QPbZxX5JzyfkDqhP-5xQ')
@click.option('--tag', '-t', help='Container tag.', default='bot:0.1')
@click.option('--build-only/--no-build-only', help='Build docker image only.', default=False)
def bot(token, tag, build_only):
    """ Deploy telegram bot. """
    print('[Deploy Telegram Bot]')
    deploy_bot_as_local_docker_daemon(token, 'telegram_bot.dockerfile.tmp', tag, build_only=build_only)


@deploy.command()
@click.option('--token', help='BOT_TOKEN value.', default='701884073:AAF9rkmy73sq6U3QPbZxX5JzyfkDqhP-5xQ')
@click.option('--tag', '-t', help='Container tag.', default='bot:0.1')
@click.option('--build-only/--no-build-only', help='Build docker image only.', default=False)
def secretary(token, tag, build_only):
    """ Deploy secretary bot. """
    print('[Deploy Secretary Bot]')
    deploy_secretary_as_local_docker_daemon(token, 'secretary_bot.dockerfile.tmp', tag, build_only=build_only)


@deploy.command()
@click.argument('data_root')
@click.argument('index_name')
@click.option('--grpc-port', help='Server port.', default=50000)
@click.option('--caption-host', help='Caption server host url/ip.', default='127.0.0.1')
@click.option('--caption-port', help='Caption server port.', default=50001)
@click.option('--indexer-host', help='Indexer server host url/ip.', default='127.0.0.1')
@click.option('--indexer-port', help='Indexer server port.', default=5000)
@click.option('--encoder-config', help='Encoder config file.', default='/tmp/encoder.json')
@click.option('--tag', '-t', help='Container tag.', default='fx-serving:0.1')
@click.option('--worker-threads', '-w', help='Max worker threads.', default=10)
@click.option('--build-only/--no-build-only', help='Build docker image only.', default=False)
def fx(data_root, index_name, grpc_port, caption_host, caption_port, indexer_host, indexer_port, encoder_config, tag,
       worker_threads, build_only):
    """ Deploy FX index serving node. """
    print('[Deploy FX Index Serving Nodes]')
    assert os.path.exists(data_root), "data_root: {} does not exist.".format(data_root)
    index_path = os.path.join(data_root, index_name)
    if not index_path.endswith('.fvec'):
        index_path = '{}.fvec'.format(index_path)
    assert os.path.exists(index_path), "--index-path `{}` does not exist. Aborting.".format(index_path)
    assert os.path.exists(encoder_config), "--encoder_config: {} does not exist.".format(encoder_config)
    print('Copying {} to {}'.format(encoder_config, data_root))
    try:
        shutil.copy(encoder_config, data_root)
    except Exception as e:
        print(e)
        pass
    args = ('--index-path=/data/{} --encoder-config=/data/{} --indexer-host={} --indexer-port={} '
            '--caption-host={} --caption-port={} --worker-threads={} --grpc-port {}'.format(
        index_name, os.path.basename(encoder_config), indexer_host, indexer_port, caption_host, caption_port,
        worker_threads, grpc_port))
    deploy_fx_serving_as_local_docker_daemon(data_root, args, 'fx-serving.dockerfile.tmp', tag, grpc_port,
                                             build_only=build_only)


@deploy.command()
@click.argument('model_dir')
@click.argument('model_name')
@click.option('--num-worker', '-w', help='Number of bert serving worker.', default=1)
@click.option('--max-batch-size', '-b', help='Bert serving max batch size.', default=16)
@click.option('--tag', '-t', help='Container tag', default='bert-serving:0.1')
@click.option('--build-only/--no-build-only', help='Build docker image only.', default=False)
def bert(model_dir, model_name, num_worker, max_batch_size, tag, build_only):
    """ Deploy BERT serving node. """
    print('[Deploy BERT serving node]')
    deploy_bert_serving_as_local_docker_daemon(
        model_dir, model_name, '-num_worker={} -max_batch_size={}'.format(num_worker, max_batch_size),
        'bert-serving.dockerfile.tmp', tag, build_only=build_only)


@deploy.command()
@click.argument('index_dir')
@click.argument('index_name')
@click.option('--encoder-host', help='Encoder host url/ip.', default='127.0.0.1')
@click.option('--encoder-port', help='Encoder host port.', default=5555)
@click.option('--grpc-port', help='Server port.', default=50000)
@click.option('--indexer-host', help='Indexer server host url/ip.', default='127.0.0.1')
@click.option('--indexer-port', help='Indexer server port.', default=5000)
@click.option('--backend-tag', '-bt', help='Indexer container tag.', default='sx-indexer:0.1')
@click.option('--frontend-tag', '-ft', help='Frontend container tag.', default='sx-serving:0.1')
@click.option('--worker-threads', '-w', help='Max worker threads.', default=10)
@click.option('--build-only/--no-build-only', help='Build docker image only.', default=False)
def sx(index_dir, index_name, encoder_host, encoder_port, grpc_port, indexer_host, indexer_port, backend_tag,
       frontend_tag, worker_threads, build_only):
    """ Deploy SX index serving node. """
    print('[Deploy SX index serving node]')
    deploy_sx_indexer_as_local_docker_daemon(
        index_dir, index_name,
        'service.ini.tmp', 'sx-indexer.dockerfile.tmp', indexer_port, backend_tag, build_only=build_only)

    indexer_ip_addresses = []
    counter = 0
    while counter < 10:
        indexer_ip_addresses = get_container_ip('sx-indexer:0.1')
        if len(indexer_ip_addresses) == 0:
            print('Waiting for indexer to start ...')
            time.sleep(3)
        else:
            break
        counter += 1

    if counter == 10:
        print('Failed to start SX indexer')
        sys.exit(1)

    args = '--encoder-host {} --encoder-port {} --indexer-host {} --indexer-port {} --worker-threads {} --grpc-port {}'.format(
        encoder_host, encoder_port, indexer_ip_addresses[0], indexer_port, worker_threads, grpc_port)

    deploy_sx_serving_as_local_docker_daemon(
        index_dir, index_name, args, 'sx-serving.dockerfile.tmp', grpc_port, frontend_tag, build_only=build_only)


@deploy.command()
@click.argument('queue_dir')
@click.option('--grpc-port', help='Server port.', default=45000)
@click.option('--tag', '-t', help='Container tag.', default='simple-queue:0.1')
@click.option('--worker-threads', '-w', help='Max worker threads.', default=10)
@click.option('--build-only/--no-build-only', help='Build docker image only.', default=False)
def queue(queue_dir, grpc_port, tag, worker_threads, build_only):
    """ Deploy Queue node. """
    print('[Deploy Queue Nodes]')
    args = ('--worker-threads={} --grpc-port {}'.format(
            worker_threads, grpc_port))
    deploy_queue_as_local_docker_daemon(
        queue_dir, args, 'queue.dockerfile.tmp', grpc_port, tag, build_only=build_only)


@cli.group()
def start():
    pass


@start.command()
def bot():
    """ Deploy Hawking Telegram Bot. """
    # TODO(oleg): deploy this as docker container
    from hawking.bot.telegram import main
    main()


@start.command()
def secretary_bot():
    """ Deploy Secretary Bot. """
    # TODO(oleg): deploy this as docker container
    from hawking.bot.secretary import main
    main()


@start.command()
@click.option('--port', '-p', help="Listening port", default=8080)
def frontend(port):
    """ Deploy Hawking front-end. """
    # TODO(oleg): deploy this as docker container
    from hawking.frontend.application import main
    main(port)


@start.command()
@click.option('--index-path', help='Path to index', default=None)
@click.option('--grpc-port', help='Server port.', default=50000)
@click.option('--caption-host', help='Caption server host url/ip.', default='127.0.0.1')
@click.option('--caption-port', help='Caption server port.', default=50001)
@click.option('--indexer-host', help='Indexer server host url/ip.', default='127.0.0.1')
@click.option('--indexer-port', help='Indexer server port.', default=5000)
@click.option('--encoder-config', help='Encoder config file.', default='/tmp/encoder.json')
@click.option('--worker-threads', '-w', help='Max worker threads.', default=10)
@click.option('--run-bot/--no-run-bot', help='Run telegram bot.', default=False)
def fx(index_path, grpc_port, caption_host, caption_port, indexer_host, indexer_port, encoder_config, worker_threads,
       run_bot):
    """ Start fx serving. """
    from hawking.serve.faiss_server import serve as fx_serve
    with open(encoder_config, 'r') as f:
        encoder_config = json.load(f)
    if not index_path.endswith('.fvec'):
        index_path = '{}.fvec'.format(index_path)
    assert os.path.exists(index_path), "--index-path `{}` does not exist. Aborting.".format(index_path)
    fx_serve(index_path, indexer_host, indexer_port, caption_host, caption_port, worker_threads, grpc_port,
             encoder_config, run_bot)


@start.command()
@click.option('--index-path', help='Path to index', default=None)
@click.option('--grpc-port', help='Server port.', default=50001)
@click.option('--worker-threads', '-w', help='Max worker threads.', default=10)
def caption(index_path, grpc_port, worker_threads):
    """ Start caption serving. """
    from hawking.serve.caption_server import serve as caption_serve
    if not index_path.endswith('.caption'):
        index_path = '{}.caption'.format(index_path)
    assert os.path.exists(index_path), "--index-path `{}` does not exist. Aborting.".format(index_path)
    caption_serve(index_path, worker_threads, grpc_port)


@cli.command()
@click.argument('doc_ids', nargs=-1)
@click.option('--server-ip', '-s', help="Remote caption host url/ip", default='127.0.0.1')
@click.option('--port', '-p', help="Remote caption server port", default=50001)
def caption(doc_ids, server_ip, port):
    """ Query Hawking caption server. """
    from hawking_proto import hawking_pb2, hawking_pb2_grpc

    with grpc.insecure_channel('{}:{}'.format(server_ip, port)) as channel:
        stub = hawking_pb2_grpc.CaptionStub(channel)
        request = hawking_pb2.SnippetRequest(max_length=200, prettify=True)
        for doc_id in doc_ids:
            request.doc_ids.append(int(doc_id))

        bold('DocIds: "{}"'.format(','.join(doc_ids)))
        st = time.time()
        response = stub.Get(request)
        bold('Caption results:\n')
        for snippet in response.snippets:
            hilite('"%s"' % snippet.title)

        et = (time.time() - st) * 1000.0
        bold('\nelapsed time: %d ms' % et)


@cli.command()
@click.option('--entity-list', '-list', help='File containing list of entities', default=None)
@click.option('--batch-size', '-b', help='Size of batch encoding request', default=500)
@click.option('--doc-count', '-n', help='Number of docs', default=100)
@click.option('--output', '-o', help='Output filename', default='hawking.em')
@click.option('--dimension', '-dim', help='Embedding dimension', default=768)
@click.option('--random-index/--no-random-index', '-r/-no-r', help='Generate random index', default=False)
@click.option('--encoder-config', help="Encoder config", default='/tmp/encoder.json')
def batch_index(entity_list, batch_size, doc_count, output, dimension, random_index, encoder_config):
    """ Create batch index (offline).

    When --random is specified, generate random index with random embedding.
    """
    from hawking.encoder import create_encoder

    if not random_index:
        assert entity_list is not None, "When --random-index is False, --entity-list argument is mandatory."
    dimension = int(dimension)
    from random import random, shuffle

    class DocumentIterator:
        def __init__(self, source_file):
            source_file = source_file
            handle = None

        def next(self):
            raise Exception('You are calling an abstract class method. Please use the derived class next().')

        source_file = ''
        _handle = None

    class TextIterator(DocumentIterator):
        def __init__(self, source_file):
            self.source_file = source_file
            self._handle = open(self.source_file, 'r')

        def next(self):
            for line in self._handle:
                yield line.strip()
            self._handle.close()

    def gen_rand_metadata():
        s = 'abc 123 ghi j#@ m$o,.?'
        l = list(s)
        shuffle(l)
        return ''.join(l)

    def gen_rand_index(p_output, p_metadata_fn, p_dim):
        """ Generate random sptag index

        format:
        <text-0>\t<v0>,...,<v-dim-1>\n
        ...
        <text-n>\t<v0>,...,<v-dim-1>\n
        """
        with open(p_output, 'w') as f:
            for i in range(doc_count):
                f.write(p_metadata_fn())
                f.write('\t')
                f.write('%f' % random())
                for n in range(p_dim - 1):
                    f.write('|')
                    f.write('%f' % random())
                f.write('\n')
        return doc_count

    def write_record(p_out, p_phrases, p_vectors, p_dim):
        """ Write record (<phrase>\t<vector>\n) to a file. """
        for i, v in enumerate(p_vectors):
            p_out.write(p_phrases[i])
            p_out.write('\t')
            assert v.size > 0 and v.size == p_dim, 'Embedding dimension does not match. Expected:{}. Actual:{}'.format(p_dim, v.size)
            value = '|'.join([repr(a) for a in v])
            p_out.write(value)
            p_out.write('\n')

    def gen_embedding_index(p_output, p_doc_iter, p_dim, p_encoder, p_batch_size=100):
        """ Generate sptag index from document list

        format:
        <text-0>\t<v0>,...,<v-p_dim-1>\n
        ...
        <text-n>\t<v0>,...,<v-p_dim-1>\n
        """
        phrases = []
        count = 0
        with open(output, 'w') as f:
            start = time.time()
            for phrase in p_doc_iter.next():
                if phrase == '' or len(phrase) == 0:
                    continue
                phrases.append(phrase)
                if len(phrases) < p_batch_size:
                    continue
                count += len(phrases)
                vectors = p_encoder.batch_encode(phrases)
                assert len(vectors) == len(phrases)
                write_record(f, phrases, vectors, p_dim)
                elapsed_secs = time.time() - start
                info('Progress: %d docs. Elapsed: %.3f s. Rate: %.2f dps ...' % (count, elapsed_secs, len(phrases)/elapsed_secs))
                vectors = []
                phrases = []
                start = time.time()

            if len(phrases) > 0:
                count += len(phrases)
                start = time.time()
                info('Indexing remaining {} docs'.format(len(phrases)))
                vectors = p_encoder.batch_encode(phrases)
                assert len(vectors) == len(phrases)
                write_record(f, phrases, vectors, p_dim)
                elapsed_secs = time.time() - start
                info('Progress: %d docs. Elapsed: %.3f s. Rate: %.2f dps ...' % (count, elapsed_secs, len(phrases)/elapsed_secs))
                vectors = []
                phrases = []
        return count

    start = time.time()
    if random_index:
        info('Generate random embedding ...')
        total_entity_count = gen_rand_index(output, gen_rand_metadata, dimension)
    else:
        info('Generate embedding file from:`{}`...'.format(entity_list))
        entity_iter = TextIterator(entity_list)
        print('Encoder Config:{}'.format(encoder_config))
        with open(encoder_config, 'r') as f:
            encoder_config = json.load(f)
        encoder = create_encoder(config=encoder_config)
        if encoder_config['entity_type'] == 'text':
            total_entity_count = gen_embedding_index(output, entity_iter, dimension, encoder, batch_size)
        elif encoder_config['entity_type'] == 'image':
            total_entity_count = gen_embedding_index(output, entity_iter, dimension, encoder, batch_size)
        else:
            raise ValueError('-t {} is not supported!'.format(encoder_config['entity_type']))
    print('Completed building index.')
    print(' Output       : %s' % output)
    print(' Total #docs  : %d' % total_entity_count)
    print(' Elapsed time : %.3f secs' % (time.time() - start))
    print(' Batch size   : %d' % batch_size)


@cli.group()
def text():
    """ Text command group. """
    pass


@text.command()
@click.argument('index')
@click.option('--embedding', 'e', help="A single atom embedding, format: <atom>\t<v0> <v1> ... <vK>", default=None)
@click.option('--embedding_file', '-ef', help='Embedding file, rows of atoms embeddings', default=None)
def index(index, embedding, embedding_file):
    """ Add atom embedding(s) to Hawking index in online manner. """
    print('[Updating embedding index]')
    if (embedding is None
            and embedding_file is None):
        raise Exception('Either --embedding or --embedding_file must be specified.')


@text.command()
@click.argument('phrases', nargs=-1)
@click.option('--encoder-host', '-e', help="Remote encoder host url/ip", default='127.0.0.1')
@click.option('--encoder-port', '-p', help="Remote encoder port", default=5555)
@click.option('--encoder-type', help="Encoder type.", default="universal-sentence-encoder")
@click.option('--weights', help="Pre-trained weights uri, it can be name or uri.",
              default="https://tfhub.dev/google/universal-sentence-encoder-multilingual-qa/1")
def encode(phrases, encoder_host, encoder_port, encoder_type, weights):
    """ Encode phrase(s) into vector embedding.

    encoder-type: online-bert
    weights: [ignored]

    encoder-type: bert
    weights: https://huggingface.co/pytorch-transformers/pretrained_models.html

    encoder-type: universal-sentence-encoder
    weights:
    - https://tfhub.dev/google/universal-sentence-encoder/2
    - https://tfhub.dev/google/universal-sentence-encoder-large/3
    - https://tfhub.dev/google/universal-sentence-encoder-lite/2
    - https://tfhub.dev/google/universal-sentence-encoder-multilingual/1
    - https://tfhub.dev/google/universal-sentence-encoder-multilingual-qa/1
    """
    from hawking.encoder import create_encoder
    encoder = create_encoder(config={
        "entity_type": "text",
        "encoder_type": encoder_type,
        "weights": weights,
        "encoder_host": encoder_host,
        "encoder_port": int(encoder_port),
    })
    for p in phrases:
        v = encoder.encode(p)
        print(v)


@text.command()
@click.argument('phrases', nargs=-1)
@click.option('--server-ip', '-s', help="Remote Hawking host url/ip", default='127.0.0.1')
@click.option('--port', '-p', help="Remote Hawking server port", default=50000)
@click.option('--result-count', '-n', help="Result count", default=10)
def query(phrases, server_ip, port, result_count):
    """ Query Hawking index server. """
    from hawking_proto import hawking_pb2, hawking_pb2_grpc

    with grpc.insecure_channel('{}:{}'.format(server_ip, port)) as channel:
        stub = hawking_pb2_grpc.SearchStub(channel)
        for phrase in phrases:
            bold('Query: "{}"'.format(phrase))
            st = time.time()
            request = hawking_pb2.SearchRequest(max_results=result_count, query=phrase,
                                                type=hawking_pb2.SearchRequest.EntityType.TEXT)
            response = stub.Get(request)
            bold('Search results:\n')
            rank = 1
            for result in response.results:
                hilite('%d. "%s" [docid:%s, score:%.6f]' % (rank, result.document.body, result.document.uuid, result.score))
                rank += 1

            et = (time.time() - st) * 1000.0
            bold('\nelapsed time: %d ms' % et)


@cli.group()
def image():
    """ Image command group. """
    pass


@image.command()
@click.argument('uris', nargs=-1)
@click.option('--arch', '-a', help="Neural Net Architecture: ['resnet50', 'vgg16', 'vgg19', 'inceptionresnetv2']", default='resnet50')
@click.option('--top-layer', '-t', help="Top layer output. resnet50:['avg_pool', 'fc1000'], "
              "inceptionresnetv2:['predictions','avg_pool']", default='fc1000')
@click.option('--print-summary/--no-print-summary', '-p/-no-p', help="To print model summary or not", default=True)
def encode(uris, arch, top_layer, print_summary):
    """ Encode image into embedding features. """
    from hawking.encoder import create_encoder
    enc = create_encoder('image', arch, config={"top_layer": top_layer, "print_summary": print_summary})

    for uri in uris:
        v = enc.encode(uri)
        print(v)
        print(v.shape)


@image.command()
@click.argument('uris', nargs=-1)
@click.option('--port', '-p', help="Port of the hawking server.", default=50000)
@click.option('--result-count', '-n', help="Result count.", default=10)
@click.option('--server-ip', '-s', help="Server IP address.", default='127.0.0.1')
def find(uris, port, result_count, server_ip):
    """ Query Hawking index server. """
    from hawking_proto import hawking_pb2, hawking_pb2_grpc

    with grpc.insecure_channel('{}:{}'.format(server_ip, port)) as channel:
        stub = hawking_pb2_grpc.SearchStub(channel)
        for uri in uris:
            bold('Find: "{}"'.format(uri))
            st = time.time()
            request = hawking_pb2.SearchRequest(max_results=result_count, query=uri,
                                                type=hawking_pb2.SearchRequest.EntityType.IMAGE)
            response = stub.Get(request)
            bold('Search results:\n')
            rank = 1
            for result in response.results:
                hilite('%d. "%s" [docid:%s, score:%.6f]' % (rank, result.document.body, result.document.uuid, result.score))
                rank += 1

            et = (time.time() - st) * 1000.0
            bold('\nelapsed time: %d ms' % et)


@cli.command()
def port_table():
    """ List port table. """
    print('IndexServing:5000')
    print('BertServing:5555')
    print('FX-Serving:50000')
    print('SX-Serving:50000')
    print('CaptionServing:50001')


@cli.command()
@click.argument('tags', nargs=-1)
def get_ip(tags):
    """ Get IP Address of containers. """
    for tag in tags:
        get_container_ip(tag)


@cli.command()
@click.argument('tags', nargs=-1)
def kill(tags):
    """ Kill containers by tag """
    for tag in tags:
        kill_container(tag)


def main():
    cli()


if __name__ == '__main__':
    main()
