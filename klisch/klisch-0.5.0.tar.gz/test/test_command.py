from klisch import command


def test_command_build():
    cmd = command.Command('python hello.py', arg_style='--')

    cmd.args = {'name': 'Eru', 'show': True}
    str_cmd = cmd.build()
    assert str_cmd == 'python hello.py --name Eru --show'

    cmd.args = {'name': 'Eru', 'show': False}
    str_cmd = cmd.build()
    assert str_cmd == 'python hello.py --name Eru'

    cmd.args = {'name': '""'}
    str_cmd = cmd.build()
    assert str_cmd == 'python hello.py --name ""'


def test_bsub_command_build_and_dry_run():
    cmd = command.Command('python hello.py', arg_style='--')
    cmd.args = {'name': 'Eru', 'show': True}

    bsub = command.BsubCommand({'q': 'GPU'}, log=True)
    str_busb = bsub.build(cmd.build(), ignore_env_bsub=True)
    assert (
        '-q GPU '
        '-o ${job_folder}/job%J_stdout.log '
        '-e ${job_folder}/job%J_stderr.log '
        '"python hello.py --name Eru --show"') in str_busb

    str_sh = bsub.run(
        cmd.build(),
        post_command='mv lv1/output output',
        environ={'PYTHONPATH': '.'},
        dry_run=True
    )
    assert (
        'export PYTHONPATH=.\n'
        'python hello.py --name Eru --show\n'
        'mv lv1/output outpu') in str_sh
