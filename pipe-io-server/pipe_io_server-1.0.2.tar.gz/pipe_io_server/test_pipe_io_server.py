# pylint: disable=redefined-outer-name
from os import stat, urandom, remove
from os.path import exists, dirname, realpath, join
from stat import S_ISFIFO
from secrets import token_urlsafe
from random import randint, getrandbits, uniform
from threading import Thread
from json import dumps, loads

import pytest

from .pipe_io_server import PipeIOServer


class EchoPipeIOServer(PipeIOServer):
    def handle_message(self, message):
        self.send_message(message)


@pytest.fixture
def io_pipes():
    with EchoPipeIOServer(*get_test_init_params()) as pipe_io:
        with IOPipes(pipe_io.in_pipe, pipe_io.out_pipe) as io_pipes:
            yield io_pipes


def get_test_init_params():
    here = dirname(realpath(__file__))
    return join(here, 'in_pipe_tests'), join(here, 'out_pipe_tests')


def teardown_module():
    for pipe in get_test_init_params():
        if exists(pipe):
            remove(pipe)


def raise_if_thread_blocks(*, target, unblock_function):
    thread = Thread(target=target)
    thread.start()
    unblock_function()
    thread.join(timeout=1)
    if thread.is_alive():
        raise RuntimeError('PipeIOServer failed to shut down!')


class IOPipes:
    def __init__(self, in_pipe_path, out_pipe_path):
        self.in_pipe_path = in_pipe_path
        self.out_pipe_path = out_pipe_path

    def __enter__(self):
        # pylint: disable=attribute-defined-outside-init
        self.in_pipe = open(self.in_pipe_path, 'wb')
        self.out_pipe = open(self.out_pipe_path, 'rb')
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def close(self):
        self.in_pipe.close()
        self.out_pipe.close()

    def send_message(self, message):
        self.in_pipe.write(message + b'\n')
        self.in_pipe.flush()

    def recv(self):
        return self.out_pipe.readline().rstrip(b'\n')


def pipes_exist(*paths):
    predicate = lambda path: exists(path) and S_ISFIFO(stat(path).st_mode)
    return all(predicate(path) for path in paths)


def test_manage_pipes():
    pipe_io = PipeIOServer(*get_test_init_params(), manage_pipes=True)
    assert pipes_exist(pipe_io.in_pipe, pipe_io.out_pipe)
    pipe_io.stop()
    assert not pipes_exist(pipe_io.in_pipe, pipe_io.out_pipe)


def test_no_manage_pipes():
    pipe_io = PipeIOServer(*get_test_init_params(), manage_pipes=False)
    assert not pipes_exist(pipe_io.in_pipe, pipe_io.out_pipe)
    pipe_io.stop()
    assert not pipes_exist(pipe_io.in_pipe, pipe_io.out_pipe)


def test_start_stop():
    pipe_io = EchoPipeIOServer(*get_test_init_params())
    pipe_io.start()
    raise_if_thread_blocks(target=pipe_io.wait, unblock_function=pipe_io.stop)


def test_start_open_stop():
    pipe_io = EchoPipeIOServer(*get_test_init_params())
    pipe_io.start()
    with IOPipes(pipe_io.in_pipe, pipe_io.out_pipe):
        raise_if_thread_blocks(target=pipe_io.wait, unblock_function=pipe_io.stop)


def test_start_open_rw_stop():
    pipe_io = EchoPipeIOServer(*get_test_init_params())
    pipe_io.start()
    with IOPipes(pipe_io.in_pipe, pipe_io.out_pipe) as iopipes:
        test_message = token_urlsafe(randint(128, 256))
        iopipes.send_message(test_message.encode())
        assert test_message == iopipes.recv().decode()
        iopipes.send_message(test_message.encode())
        raise_if_thread_blocks(target=pipe_io.wait, unblock_function=pipe_io.stop)


def test_start_open_brokenpipe_stop():
    pipe_io = EchoPipeIOServer(*get_test_init_params())
    pipe_io.start()
    with IOPipes(pipe_io.in_pipe, pipe_io.out_pipe) as iopipes:
        iopipes.out_pipe.close()
        test_message = token_urlsafe(randint(128, 256))
        iopipes.send_message(test_message.encode())
        with pytest.raises(ValueError):
            iopipes.recv()
        raise_if_thread_blocks(target=pipe_io.wait, unblock_function=pipe_io.stop)


def test_start_open_eof_stop():
    pipe_io = EchoPipeIOServer(*get_test_init_params())
    pipe_io.start()
    with IOPipes(pipe_io.in_pipe, pipe_io.out_pipe) as iopipes:
        iopipes.in_pipe.close()
        test_message = token_urlsafe(randint(128, 256))
        with pytest.raises(ValueError):
            iopipes.send_message(test_message.encode())
        raise_if_thread_blocks(target=pipe_io.wait, unblock_function=pipe_io.stop)


def test_start_open_delete_pipes_stop():
    pipe_io = EchoPipeIOServer(*get_test_init_params())
    pipe_io.start()
    with IOPipes(pipe_io.in_pipe, pipe_io.out_pipe):
        remove(pipe_io.in_pipe)
        remove(pipe_io.out_pipe)
        raise_if_thread_blocks(target=pipe_io.wait, unblock_function=pipe_io.stop)


@pytest.mark.parametrize(
    'test_data', [
        'Cats and cheese',
        'You ever wonder why we are here?',
        'Lorem ipsum dolor sit amet',
        'You always have a plan, Dutch!',
    ]
)
def test_io(io_pipes, test_data):
    io_pipes.send_message(test_data.encode())
    assert io_pipes.recv().decode() == test_data


def test_io_random(io_pipes):
    test_data = token_urlsafe(512)
    for _ in range(100):
        io_pipes.send_message(test_data.encode())
        assert io_pipes.recv().decode() == test_data

@pytest.mark.parametrize(
    'test_data_size', [
        1024,
        1024*1024,
        2*1024*1024,
        4*1024*1024,
        8*1024*1024,
        16*1024*1024,
    ]
)
def test_io_large_data(io_pipes, test_data_size):
    test_data = urandom(test_data_size).replace(b'\n', b'')
    io_pipes.send_message(test_data)
    received_data = io_pipes.recv()
    assert received_data == test_data


def test_io_stress(io_pipes):
    for _ in range(2222):
        test_data = urandom(randint(1, 1024)).replace(b'\n', b'')
        io_pipes.send_message(test_data)
        assert io_pipes.recv() == test_data


def test_io_newlines(io_pipes):
    times = randint(1, 512)
    io_pipes.send_message(b'\n' * times)
    for _ in range(times + 1):  # IOPipes.send appends +1
        assert io_pipes.recv() == b''


def test_json_io(io_pipes):
    for _ in range(10):
        test_data = {
            f'{token_urlsafe(8)}': randint(1, 2 ** 20),
            f'{token_urlsafe(9)}': [randint(1, 2 **10) for i in range(10)],
            f'{token_urlsafe(4)}': f'{token_urlsafe(8)}\\\n{token_urlsafe(8)}\n{randint(1, 2 ** 10)}',
            f'{token_urlsafe(11)}': {
                f'{token_urlsafe(8)}': '',
                f'{token_urlsafe(3)}': f'{token_urlsafe(8)}\n{token_urlsafe(8)}\n\\n{token_urlsafe(8)}',
                f'{token_urlsafe(44)}': f'{token_urlsafe(8)}\n{token_urlsafe(8)}  {token_urlsafe(8)}',
                f'{token_urlsafe(6)}\n{token_urlsafe(4)}': bool(getrandbits(1)),
                f'{token_urlsafe(8)}': None,
                f'{token_urlsafe(21)}  {token_urlsafe(4)}': None,
                f'{token_urlsafe(3)}': uniform(randint(1, 100), randint(1, 100)),
                f'{token_urlsafe(8)}': [token_urlsafe(4) for i in range(10)],
            }
        }
        io_pipes.send_message(dumps(test_data).encode())
        assert loads(io_pipes.recv()) == test_data


def test_assign_message_handler():
    pipe_io = PipeIOServer(*get_test_init_params())
    pipe_io.handle_message = lambda msg: pipe_io.send_message(msg * 2)
    with pipe_io, IOPipes(pipe_io.in_pipe, pipe_io.out_pipe) as io_pipes:
        for _ in range(100):
            test_data = token_urlsafe(32).encode()
            io_pipes.send_message(test_data)
            assert io_pipes.recv() == test_data * 2


def test_write_immediately():
    for _ in range(10):
        pipe_io = PipeIOServer(*get_test_init_params())
        with pipe_io:
            pipe_io.send_message(b'cica')
