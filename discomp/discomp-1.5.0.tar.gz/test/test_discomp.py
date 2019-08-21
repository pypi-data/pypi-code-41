import os
import shutil
import sys

import dill
import subprocess
import unittest
import func_examples

if sys.version_info >= (3, 0):
    from unittest.mock import patch
    from io import StringIO
else:
    from StringIO import StringIO
    from mock import patch


from discomp import Process
from discomp import Pool


class TestProcess(unittest.TestCase):

    def setUp(self):
        if not os.path.exists("run-result"):
            os.mkdir("run-result")

    def tearDown(self):
        if os.path.exists("customer-module.pickle"):
            os.remove("customer-module.pickle")
        if os.path.exists("result.pickle"):
            os.remove("result.pickle")
        inter_dirs = [a for a in os.listdir(os.getcwd()) if a.startswith("interm")]
        for d in inter_dirs:
            if os.path.exists(d):
                shutil.rmtree(d)


    @patch('sys.stdout', new_callable=StringIO)
    @patch('discomp.utils.subprocess_send_command')
    def test_disco_is_uninstalled(self, mock_os_error, mock_stdout):
        mock_os_error.side_effect = OSError(2, 'Some error')

        os.environ['DISCO_LOGIN_USER'] = 'user@dis.co'
        os.environ['DISCO_LOGIN_PASSWORD'] = 'password'

        p1 = Process(
            name='abcdjob',
            target=func_examples.mult,
            args=(3, 7))
        assert ('Dis.co is not installed, Please install it first.' in mock_stdout.getvalue())

        self.assertEqual(p1.job_id, '')
        self.assertEqual(p1.job_status, 'JobStatus.init')

    @patch('discomp.utils.send_command')
    def test_login(self, mock_utils_send_command):

        return_value1 = 'Logged in as user@dis.co'
        return_value2 = ".\n Job created successfully!\njobId: [5c3b489df0f9c8000768e195]\n"

        mock_utils_send_command.side_effect = [return_value1, return_value2]

        os.environ['DISCO_LOGIN_USER'] = 'user@dis.co'
        os.environ['DISCO_LOGIN_PASSWORD'] = 'password'

        p1 = Process(
            name='abcdjob',
            target=func_examples.mult,
            args=(3, 7))

        self.assertTrue(mock_utils_send_command.called)
        self.assertEqual(mock_utils_send_command.call_count, 2)
        expected = ((['disco', 'login', '-u', 'user@dis.co', '-p', 'password'], False),)
        self.assertTrue(mock_utils_send_command.call_args_list[0] == expected)

    @patch('discomp.disco_cli_wrapper.disco_login')
    def test_login_failure(self, mock_disco_login):

        mock_disco_login.return_value = False

        p1 = Process(
            name='abcdjob',
            target=func_examples.mult,
            args=(3, 7))

        self.assertTrue(mock_disco_login.called)
        self.assertEqual(p1.job_id, '')
        self.assertEqual(p1.job_status, 'JobStatus.init')

    @patch('discomp.job_file_handler.remove_input_files')
    @patch('discomp.job_file_handler.remove_script_file')
    @patch('sys.stdout', new_callable=StringIO)
    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_create_process(self, mock_disco_cli, mock_stdout, mock_remove_script_file, mock_remove_input_files):
        mock_disco_cli.return_value = "Uploaded all assets.\n Job created successfully!\njobId: [5c3b489df0f9c8000768e195]\n"
        mock_remove_script_file.return_value = True
        mock_remove_input_files.return_value = True

        args = (3, 7)
        p1 = Process(
            name='abcdjob',
            target=func_examples.mult,
            args=args)

        inter_dirs = [a for a in os.listdir(os.getcwd()) if a.startswith("interm")]
        shutil.copy2('func_examples.py', inter_dirs[0])
        python_version = 'python3' if sys.version_info >= (3, 0) else 'python2'
        script_file_name = p1.job_name + '-script.py'
        result1 = subprocess.check_output(
            [python_version, inter_dirs[0] + "/" + script_file_name, inter_dirs[0] + "/" + "input-data0.pickle", "customer-module.pickle"]).decode("utf-8")
        result2 = str(func_examples.mult(*args)) + '\n'

        self.assertEqual(result1, result2)
        self.assertTrue(mock_disco_cli.called)
        self.assertEqual(mock_disco_cli.call_count, 1)
        expected = ((['disco', 'add', '-n', p1.job_name, '-s', inter_dirs[0] + "/" + script_file_name, '-i', inter_dirs[0] + "/" + 'input-data*', '-t',
                      'customer-module.pickle', '-t', 'requirements.txt'], True, ''),)
        self.assertTrue(mock_disco_cli.call_args == expected)
        self.assertEqual(p1.job_id, '5c3b489df0f9c8000768e195')
        self.assertEqual(p1.job_status, 'JobStatus.created')

        # files removal was mocked, remove them here
        if os.path.exists(script_file_name):
            os.remove(script_file_name)

    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_start_process(self, mock_disco_cli):
        return_value1 = ".\n Job created successfully!\njobId: [5c3b489df0f9c8000768e195]\n"
        return_value2 = "Job started successfully!\n"

        mock_disco_cli.side_effect = [return_value1, return_value2]

        p1 = Process(
            name='abcdjob',
            target=func_examples.mult,
            args=(3, 7))

        p1.start()

        self.assertEqual(mock_disco_cli.call_count, 2)
        expected = ((['disco', 'start', '-j', '5c3b489df0f9c8000768e195'],),)
        self.assertTrue(mock_disco_cli.call_args == expected)
        self.assertEqual(p1.job_status, 'JobStatus.started')

    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_process_empty_args(self, mock_disco_cli):
        return_value1 = ".\n Job created successfully!\njobId: [5c3b489df0f9c8000768e195]\n"

        mock_disco_cli.side_effect = [return_value1]

        p1 = Process(
            name='abcdjob',
            target=func_examples.hello)

        self.assertEqual(mock_disco_cli.call_count, 1)
        self.assertEqual(p1.job_status, 'JobStatus.created')

    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_start_process_create_failed(self, mock_disco_cli):
        return_value1 = ".\n Job creation failed\n"

        p1 = Process(
            name='abcdjob',
            target=func_examples.mult,
            args=(3, 7))

        p1.start()

        self.assertEqual(mock_disco_cli.call_count, 1)
        self.assertEqual(p1.job_id, '')
        self.assertEqual(p1.job_status, 'JobStatus.init')

    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_join_process(self, mock_disco_cli):
        return_value1 = ".\n Job created successfully!\njobId: [5c3b489df0f9c8000768e195]\n"
        return_value2 = "Job started successfully!\n"
        return_value3 = "Status: Done\n Success: 1 (100%)"
        return_value4 = "Successfully downloaded task and its results into 'abcdjob'!"

        mock_disco_cli.side_effect = [return_value1, return_value2, return_value3, return_value4]

        p1 = Process(
            name='abcdjob',
            target=func_examples.mult,
            args=(3, 7))

        p1.start()
        p1.join()

        self.assertEqual(mock_disco_cli.call_count, 4)
        expected = ((['disco', 'view', '-j', '5c3b489df0f9c8000768e195', '-d'], True, 'Yes'),)
        self.assertTrue(mock_disco_cli.call_args == expected)
        self.assertEqual(p1.job_status, 'JobStatus.done')

    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_join_process_after_create_fail(self, mock_disco_cli):
        return_value1 = ".\n Job creation failed\n"

        p1 = Process(
            name='abcdjob',
            target=func_examples.mult,
            args=(3, 7))

        p1.start()
        p1.join()

        self.assertEqual(mock_disco_cli.call_count, 1)
        self.assertEqual(p1.job_id, '')
        self.assertEqual(p1.job_status, 'JobStatus.init')

    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_join_process_after_start_fail(self, mock_disco_cli):
        return_value1 = ".\n Job created successfully!\njobId: [5c3b489df0f9c8000768e195]\n"
        return_value2 = "Job failed to start!\n"

        mock_disco_cli.side_effect = [return_value1, return_value2]

        p1 = Process(
            name='abcdjob',
            target=func_examples.mult,
            args=(3, 7))

        p1.start()
        p1.join()

        self.assertEqual(mock_disco_cli.call_count, 2)
        self.assertNotEqual(p1.job_id, '')
        self.assertEqual(p1.job_status, 'JobStatus.created')

    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_join_process_with_job_failed(self, mock_disco_cli):
        return_value1 = ".\n Job created successfully!\njobId: [5c3b489df0f9c8000768e195]\n"
        return_value2 = "Job started successfully!\n"
        return_value3 = "Status: Done\n Failure: 1 (100%)"
        return_value4 = "Status: Done\n Failure: 1 (100%)"

        mock_disco_cli.side_effect = [return_value1, return_value2, return_value3, return_value4]

        p1 = Process(
            name='abcdjob',
            target=func_examples.mult,
            args=(3, 7))

        p1.start()
        p1.join()

        self.assertEqual(mock_disco_cli.call_count, 4)
        expected = ((['disco', 'view', '-j', '5c3b489df0f9c8000768e195'],),)
        self.assertTrue(mock_disco_cli.call_args == expected)
        self.assertEqual(p1.job_status, 'JobStatus.done')

    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_start_process_twice(self, mock_disco_cli):
        return_value1 = ".\n Job created successfully!\njobId: [5c3b489df0f9c8000768e195]\n"
        return_value2 = "Job started successfully!\n"

        mock_disco_cli.side_effect = [return_value1, return_value2]

        p1 = Process(
            name='abcdjob',
            target=func_examples.mult,
            args=(3, 7))

        p1.start()
        p1.start()

        self.assertEqual(mock_disco_cli.call_count, 2)
        self.assertEqual(p1.job_status, 'JobStatus.started')

    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_join_process_twice(self, mock_disco_cli):
        return_value1 = ".\n Job created successfully!\njobId: [5c3b489df0f9c8000768e195]\n"
        return_value2 = "Job started successfully!\n"
        return_value3 = "Status: Done\n Success: 1 (100%)"
        return_value4 = "Successfully downloaded task and its results into 'abcdjob'!"

        mock_disco_cli.side_effect = [return_value1, return_value2, return_value3, return_value4]

        p1 = Process(
            name='abcdjob',
            target=func_examples.mult,
            args=(3, 7))

        p1.start()
        p1.join()
        p1.join()

        self.assertEqual(mock_disco_cli.call_count, 4)
        self.assertEqual(p1.job_status, 'JobStatus.done')

    def test_create_process_invalid_params(self):
        with self.assertRaises(ValueError):
            p1 = Process(
                name=1,
                target=func_examples.mult,
                args=(3, 7))

        with self.assertRaises(ValueError):
            p1 = Process(
                name='abcdjob',
                target='not a func',
                args=(3, 7))

        with self.assertRaises(ValueError):
            p1 = Process(
                name='abcdjob',
                target=func_examples.mult,
                args=(3))  # not a tupple

    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_process_stubs(self, mock_disco_cli):

        return_value1 = ".\n Job created successfully!\njobId: [5c3b489df0f9c8000768e195]\n"
        return_value2 = "Job started successfully!\n"

        mock_disco_cli.side_effect = [return_value1, return_value2]

        p1 = Process(
            name='abcdjob',
            target=func_examples.mult,
            args=(3, 7))

        p1.start()

        with self.assertRaises(NotImplementedError):
            p1.terminate()
        with self.assertRaises(NotImplementedError):
            p1.kill()
        with self.assertRaises(NotImplementedError):
            p1.close()


    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_map(self, mock_disco_cli):
        return_value1 = "Successfully downloaded task and its results into 'abcdjob'!"

        mock_disco_cli.side_effect = [return_value1]

        mypool = Pool()
        results = mypool.map(func_examples.pow3, range(10))
        script_file_name = mypool.job_name + '-script.py'
        self.assertEqual(mock_disco_cli.call_count, 1)
        expected = ((['disco', 'add', '-n', mypool.job_name, '-s', script_file_name, '-i', 'input-data*', '-t',
                      'customer-module.pickle', '-t', 'requirements.txt', '-w', '-d'], True, 'Yes'),)
        self.assertEqual(mock_disco_cli.call_args[0][0][0:4], expected[0][0][0:4])
        self.assertEqual(mock_disco_cli.call_args[0][0][6:7], expected[0][0][6:7])
        self.assertEqual(mock_disco_cli.call_args[0][0][9:], expected[0][0][9:])

    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_map_empty_args(self, mock_disco_cli):
        return_value1 = "Successfully downloaded task and its results into 'abcdjob'!"

        mock_disco_cli.side_effect = [return_value1]

        mypool = Pool()
        results = mypool.map(func_examples.hello, '')
        script_file_name = mypool.job_name + '-script.py'
        self.assertEqual(mock_disco_cli.call_count, 1)
        expected = ((['disco', 'add', '-n', mypool.job_name, '-s', script_file_name, '-i', 'input-data*', '-t',
                      'customer-module.pickle', '-t', 'requirements.txt', '-w', '-d'], True, 'Yes'),)
        self.assertEqual(mock_disco_cli.call_args[0][0][0:4], expected[0][0][0:4])
        self.assertEqual(mock_disco_cli.call_args[0][0][6:7], expected[0][0][6:7])
        self.assertEqual(mock_disco_cli.call_args[0][0][9:], expected[0][0][9:])

    @patch('discomp.job_file_handler.remove_input_files')
    @patch('discomp.job_file_handler.remove_script_file')
    @patch('sys.stdout', new_callable=StringIO)
    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_map_with_files(self, mock_disco_cli, mock_stdout, mock_remove_script_file, mock_remove_input_files):
        mock_disco_cli.return_value = "Uploaded all assets.\n Job created successfully!\njobId: [5c3b489df0f9c8000768e195]\n"
        mock_remove_script_file.return_value = True
        mock_remove_input_files.return_value = True

        mypool = Pool()
        results = mypool.map(func_examples.pow3, [3])
        inter_dirs = [a for a in os.listdir(os.getcwd()) if a.startswith("interm")]
        shutil.copy2('func_examples.py', inter_dirs[0])
        script_file_name = mypool.job_name + '-script.py'
        python_version = 'python3' if sys.version_info >= (3, 0) else 'python2'
        result1 = subprocess.check_output(
            [python_version, inter_dirs[0] + "/" + script_file_name, inter_dirs[0] + "/input-data0.pickle", "customer-module.pickle"]).decode("utf-8")
        result2 = str(func_examples.pow3(*(3,))) + '\n'

        self.assertEqual(result1, result2)

        # files removal was mocked, remove them here
        if os.path.exists(script_file_name):
            os.remove(script_file_name)

    @patch('discomp.job_file_handler.remove_input_files')
    @patch('discomp.job_file_handler.remove_script_file')
    @patch('sys.stdout', new_callable=StringIO)
    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_starmap_with_files_and_context_manager(self, mock_disco_cli, mock_stdout, mock_remove_script_file,
                                                    mock_remove_input_files):
        mock_disco_cli.return_value = "Uploaded all assets.\n Job created successfully!\njobId: [5c3b489df0f9c8000768e195]\n"
        mock_remove_script_file.return_value = True
        mock_remove_input_files.return_value = True

        with Pool(processes=3) as mypool:
            results = mypool.starmap(func_examples.mult, [[3, 4], [5, 6]])

        inter_dirs = [a for a in os.listdir(os.getcwd()) if a.startswith("interm")]
        shutil.copy2('func_examples.py', inter_dirs[0])
        script_file_name = mypool.job_name + '-script.py'
        python_version = 'python3' if sys.version_info >= (3, 0) else 'python2'
        result1 = subprocess.check_output(
            [python_version, inter_dirs[0] + "/" + script_file_name, inter_dirs[0] + "/" + "input-data0.pickle", "customer-module.pickle"]).decode("utf-8")
        result2 = str(func_examples.mult(*(3, 4))) + '\n'
        result3 = subprocess.check_output(
            [python_version, inter_dirs[0] + "/" + script_file_name, inter_dirs[0] + "/" + "input-data1.pickle", "customer-module.pickle"]).decode("utf-8")
        result4 = str(func_examples.mult(*(5, 6))) + '\n'

        self.assertEqual(result1, result2)
        self.assertEqual(result3, result4)

        # files removal was mocked, remove them here
        if os.path.exists(script_file_name):
            os.remove(script_file_name)


    @patch('discomp.job_file_handler.remove_input_files')
    @patch('discomp.job_file_handler.remove_script_file')
    @patch('sys.stdout', new_callable=StringIO)
    @patch('discomp.disco_cli_wrapper.disco_cli')
    def test_starmap_nested_functions(self, mock_disco_cli, mock_stdout, mock_remove_script_file,
                                      mock_remove_input_files):
        mock_disco_cli.return_value = "Uploaded all assets.\n Job created successfully!\njobId: [5c3b489df0f9c8000768e195]\n"
        mock_remove_script_file.return_value = True
        mock_remove_input_files.return_value = True

        with Pool(processes=3) as mypool:
            results = mypool.starmap(func_examples.mult_wrapper, ((3, 4), (5, 6)))

        inter_dirs = [a for a in os.listdir(os.getcwd()) if a.startswith("interm")]
        shutil.copy2('func_examples.py', inter_dirs[0])
        script_file_name = mypool.job_name + '-script.py'
        python_version = 'python3' if sys.version_info >= (3, 0) else 'python2'
        result1 = subprocess.check_output(
            [python_version, inter_dirs[0] + "/" + script_file_name, inter_dirs[0] + "/" + "input-data0.pickle", "customer-module.pickle"]).decode("utf-8")
        with open("run-result/result.pickle", "rb") as f_result:
            result = dill.load(f_result)
            self.assertEqual(result1, str(result) + '\n')

        result2 = str(func_examples.mult_wrapper(*(3, 4))) + '\n'
        result3 = subprocess.check_output(
            [python_version, inter_dirs[0] + "/" + script_file_name, inter_dirs[0] + "/" + "input-data1.pickle", "customer-module.pickle"]).decode("utf-8")
        with open("run-result/result.pickle", "rb") as f_result:
            result = dill.load(f_result)
            self.assertEqual(result3, str(result) + '\n')
        result4 = str(func_examples.mult_wrapper(*(5, 6))) + '\n'

        self.assertEqual(result1, result2)
        self.assertEqual(result3, result4)

        # files removal was mocked, remove them here
        if os.path.exists(script_file_name):
            os.remove(script_file_name)

    @patch('discomp.job_handler.add_job')
    @patch('discomp.utils.get_unique_job_name')
    def test_map_get_result(self, mock_get_unique_job_name, mock_add_job):
        mock_get_unique_job_name.return_value = 'pow31549832775.57'
        mock_add_job.return_value = True

        mypool = Pool()
        # The execution of mypool.map is ignored,
        # Instead, execute pool.get_results of a prepared directory ('5c60926e80773800072e8811-pow31549832775.57')
        results = mypool.map(func_examples.pow3, range(10))
        self.assertEqual(results, [x ** 3 for x in range(10)])

    @patch('discomp.job_handler.add_job')
    def test_map_get_result_of_failed_job(self, mock_add_job):
        mock_add_job.return_value = False

        mypool = Pool()
        results = mypool.map(func_examples.pow3, range(10))
        self.assertEqual(results, ['' for i in range(10)])

    def test_map_invalid_params(self):
        with self.assertRaises(ValueError):
            mypool = Pool()
            mypool.map('not a function', range(10))

        with self.assertRaises(ValueError):
            mypool = Pool()
            mypool.map(func_examples.pow3, 9)

    def test_starmap_invalid_params(self):
        with self.assertRaises(ValueError):
            mypool = Pool()
            mypool.map('not a function', [[3, 4], [5, 6]])

        with self.assertRaises(ValueError):
            mypool = Pool()
            mypool.starmap(func_examples.pow3, 9)

        with self.assertRaises(ValueError):
            mypool = Pool()
            mypool.starmap(func_examples.pow3, range(10))

    def test_pool_stubs(self):
        with self.assertRaises(NotImplementedError):
            mypool = Pool()
            mypool.join()
        with self.assertRaises(NotImplementedError):
            mypool = Pool()
            mypool.apply(func_examples.pow3)
        with self.assertRaises(NotImplementedError):
            mypool = Pool()
            mypool.apply_async(func_examples.pow3)
        with self.assertRaises(NotImplementedError):
            mypool = Pool()
            mypool.map_async(func_examples.pow3, range(10))
        with self.assertRaises(NotImplementedError):
            mypool = Pool()
            mypool.starmap_async(func_examples.pow3, range(10))
        with self.assertRaises(NotImplementedError):
            mypool = Pool()
            mypool.imap(func_examples.pow3, range(10))
        with self.assertRaises(NotImplementedError):
            mypool = Pool()
            mypool.imap_unordered(func_examples.pow3, range(10))


if __name__ == '__main__':
    unittest.main()
