import karantools as kt
import pytest
import mock

def test_average_simple():
	assert(kt.average([1, 2, 3]) == 2)
	assert(kt.average([1]) == 1)
	assert(kt.average([1, 2, 3, 4]) == 2.5)

	with pytest.raises(ZeroDivisionError):
		kt.average([])

def test_average_or_0():
	assert(kt.average_or_0([1, 2, 3]) == 2)
	assert(kt.average_or_0([1]) == 1)
	assert(kt.average_or_0([1, 2, 3, 4]) == 2.5)

	assert(kt.average_or_0([]) == 0)

def test_average_streamer():
	streamer = kt.AverageStreamer()

	0, 1, 3, 6, 10, 15, 21
	averages = [0, 0.5, 1, 1.5, 2, 2.5, 3]

	with pytest.raises(ZeroDivisionError):
		streamer.query()

	for i in range(7):
		streamer.add(i)
		assert(streamer.query() == averages[i])

def test_max_streamer():
	streamer = kt.MaxStreamer()

	with pytest.raises(RuntimeError):
		streamer.query()

	for i in range(0, 10):
		streamer.add(i)
		assert(streamer.query() == i)

	for i in range(9, -1, -1):
		streamer.add(i)
		assert(streamer.query() == 9)

def test_min_streamer():
	streamer = kt.MinStreamer()

	with pytest.raises(RuntimeError):
		streamer.query()

	for i in range(0, 10):
		streamer.add(i)
		assert(streamer.query() == 0)

	for i in range(9, -1, -1):
		streamer.add(i)
		assert(streamer.query() == 0)

	for i in range(-1, -10, -1):
		streamer.add(i)
		assert(streamer.query() == i)

def test_max_score_streamer():
	streamer = kt.MaxScoreStreamer(lambda x: x)

	with pytest.raises(RuntimeError):
		streamer.query()

	with pytest.raises(RuntimeError):
		streamer.query_score()

	for i in range(0, 10):
		streamer.add(i)
		assert(streamer.query() == i)
		assert(streamer.query_score() == i)

	for i in range(9, -1, -1):
		streamer.add(i)
		assert(streamer.query() == 9)
		assert(streamer.query_score() == 9)

	streamer = kt.MaxScoreStreamer(lambda x: -x)

	with pytest.raises(RuntimeError):
		streamer.query()

	with pytest.raises(RuntimeError):
		streamer.query_score()

	for i in range(0, 10):
		streamer.add(i)
		assert(streamer.query() == 0)
		assert(streamer.query_score() == 0)

	for i in range(9, -1, -1):
		streamer.add(i)
		assert(streamer.query() == 0)
		assert(streamer.query_score() == 0)

	for i in range(-1, -10, -1):
		streamer.add(i)
		assert(streamer.query() == i)
		assert(streamer.query_score() == -i)

	streamer = kt.MaxScoreStreamer(lambda x: -1 * abs(x - 5.5))

	with pytest.raises(RuntimeError):
		streamer.query()

	with pytest.raises(RuntimeError):
		streamer.query_score()

	for i in range(0, 6):
		streamer.add(i)
		assert(streamer.query() == i)
		assert(streamer.query_score() == i - 5.5)

	for i in range(6, 10):
		streamer.add(i)
		assert(streamer.query() == 5)
		assert(streamer.query_score() == -0.5)

def test_assert_and_print(capfd):
	kt.assert_and_print(1, 1 > 0)
	out, err = capfd.readouterr()
	assert(out == "1\n")

	kt.assert_and_print(1, 1 >= 0)
	out, err = capfd.readouterr()
	assert(out == "1\n")

	kt.assert_and_print(1, 1 >= 1)
	out, err = capfd.readouterr()
	assert(out == "1\n")

	test_list = [1, 2, 3]
	kt.assert_and_print(test_list, kt.average(test_list) == 2)
	out, err = capfd.readouterr()
	assert(out == "[1, 2, 3]\n")

	with pytest.raises(AssertionError):
		test_list = [1, 2, 3]
		kt.assert_and_print(test_list, kt.average(test_list) == 3)

def test_assert_eq():
	with pytest.raises(AssertionError):
		kt.assert_eq(1, 2)

	with pytest.raises(AssertionError):
		kt.assert_eq(1, [])

	with pytest.raises(AssertionError):
		kt.assert_eq(0, [])

	kt.assert_eq(1, 1)

def test_assert_float_eq():
	with pytest.raises(AssertionError):
		kt.assert_float_eq(1, 2)

	with pytest.raises(AssertionError):
		kt.assert_float_eq(1, 1 + 1e-3)

	kt.assert_float_eq(1, 1 + 1e-10)

def test_assert_neq():
	kt.assert_neq(1, 2)

	kt.assert_neq(1, [])

	kt.assert_neq(0, [])

	with pytest.raises(AssertionError):
		kt.assert_neq(1, 1)

def test_assert_float_neq():
	kt.assert_float_neq(1, 2)

	kt.assert_float_neq(1, 1 + 1e-3)

	with pytest.raises(AssertionError):
		kt.assert_float_neq(1, 1 + 1e-10)

def test_read_lines():
	lines = kt.read_lines('test_file.txt', lambda x: x.strip().split())
	lines_expected = [
		['word1', 'word2'],
		['word1', 'word3'],
		['word', '1', 'word', '2'],
		['words', 'next']
	]
	assert(lines == lines_expected)

	def map_line(line):
		line = line.strip().split()
		for i in range(len(line)):
			try:
				line[i] = float(line[i])
			except ValueError:
				pass
		return line

	lines = kt.read_lines('test_file.txt', map_line)
	lines_expected = [
		['word1', 'word2'],
		['word1', 'word3'],
		['word', 1, 'word', 2],
		['words', 'next']
	]

	assert(lines == lines_expected)

def test_time(capfd):
	with pytest.raises(RuntimeError):
		kt.time.end()

	kt.time.start('My task')
	kt.time.end()

	out, err = capfd.readouterr()

	assert('My task completed in' in out)

	kt.time.start()
	kt.time.end()

	out, err = capfd.readouterr()

	assert('Task completed in' in out)

	kt.time.start()
	kt.time.end(silent=True)

	out, err = capfd.readouterr()

	assert(not out)

	kt.time.print_times()
	out, err = capfd.readouterr()

	assert(len(out.split('\n')) == 5)

def test_print_bold(capfd):
	kt.print_bold('hello world')
	out, err = capfd.readouterr()
	assert(out == kt.colors.BOLD + 'hello world' + kt.colors.END + '\n')

def test_print_comment_header_block(capfd):

	length = 70
	kt.print_comment_header_block('HELLO WORLD')

	out, err = capfd.readouterr()
	assert(out == "#" * 70 + '\n#' + ' ' * 28 + 'HELLO WORLD' + ' ' * 29 + '#\n' + "#" * 70 + '\n')

	length = 80
	kt.print_comment_header_block('HELLO WORLD', length=length)

	out, err = capfd.readouterr()
	assert(out == "#" * 80 + '\n#' + ' ' * 33 + 'HELLO WORLD' + ' ' * 34 + '#\n' + "#" * 80 + '\n')

	length = 80
	kt.print_comment_header_block('HELLOHELLO' * 10, length=length)

	out, err = capfd.readouterr()
	assert(out == "#" * 102 + '\n#' + ' ' * 0 + 'HELLOHELLO' * 10 + ' ' * 0 + '#\n' + "#" * 102 + '\n')

	length = 80
	kt.print_comment_header_block('HELLOHELLO' * 10, length=length, adjust_length=False)

	out, err = capfd.readouterr()
	assert(out == "#" * 80 + '\n#' + ' ' * 0 + 'HELLOHELLO' * 10 + ' ' * 0 + '#\n' + "#" * 80 + '\n')

def test_print_header_block(capfd):

	length = 80
	kt.print_header_block('HELLO WORLD')

	out, err = capfd.readouterr()
	assert(out == "-" * 80 + '\n' + kt.colors.BOLD + ' ' * 34 + 'HELLO WORLD' + ' ' * 35 + kt.colors.END + '\n' + "-" * 80 + '\n')

	length = 90
	kt.print_header_block('HELLO WORLD', length=length)

	out, err = capfd.readouterr()
	assert(out == "-" * 90 + '\n' + kt.colors.BOLD + ' ' * 39 + 'HELLO WORLD' + ' ' * 40 + kt.colors.END + '\n' + "-" * 90 + '\n')

	length = 90
	kt.print_header_block('HELLOHELLO' * 10, length=length)

	out, err = capfd.readouterr()
	assert(out == "-" * 102 + '\n' + kt.colors.BOLD + ' ' + 'HELLOHELLO' * 10 + ' ' + kt.colors.END + '\n' + "-" * 102 + '\n')

	length = 90
	kt.print_header_block('HELLOHELLO' * 10, length=length, adjust_length=False)

	out, err = capfd.readouterr()
	assert(out == "-" * 90 + '\n' + kt.colors.BOLD + 'HELLOHELLO' * 10 + kt.colors.END + '\n' + "-" * 90 + '\n')

def test_suppress_stdout(capfd):

	def print_hello_world():
		print('hello world')

	print_hello_world()

	out, err = capfd.readouterr()
	assert(out == "hello world\n")

	with kt.suppress_stdout():
		print_hello_world()

	out, err = capfd.readouterr()
	assert(not out)

def test_run_command(capfd):
	assert(kt.run_command('true') == 0)
	out, err = capfd.readouterr()
	assert('true' in out)

	assert(kt.run_command('echo "hi"') == 0)
	out, err = capfd.readouterr()
	assert('echo "hi"' in out)

	assert(kt.run_command('false', ignore_error=True) != 0)
	out, err = capfd.readouterr()
	assert('false' in out)
	assert('Error' in out)