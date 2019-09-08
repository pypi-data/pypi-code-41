import io
import tempfile

from klisch import env, files


class Command:

    def __init__(self, app: str, arg_style: str = '-') -> None:
        self.app = app
        self.arg_style = arg_style
        self.args = {}

    def build(self) -> str:
        cmd_args = []
        for key, val in self.args.items():
            if not val:
                continue
            arg_name = f'{self.arg_style}{key}'
            if isinstance(val, bool):
                cmd_args.append(arg_name)
            else:
                cmd_args.append(f'{arg_name} {val}')

        args_line = ' '.join(cmd_args)
        return f'{self.app} {args_line}'


class BsubCommand:

    def __init__(self, lsf_options, log=False):
        self.lsf_options = lsf_options
        self.log = log

    def build(
        self, command: str, interactive: bool = False, job_folder: str = '',
        ignore_env_bsub: bool = False
    ) -> str:
        if not ignore_env_bsub and not env.BSUB:
            print('Fallback to normal command')
            return command

        cmd = Command(app='bsub')
        if self.log:
            self.lsf_options.update(
                {
                    'o': '${job_folder}/job%J_stdout.log',
                    'e': '${job_folder}/job%J_stderr.log',
                }
            )
        cmd.args = self.lsf_options
        if interactive:
            cmd.args['Is'] = True
            del cmd.args['o']
            del cmd.args['e']
        bsub_pre = cmd.build()
        return bsub_pre + f' "{command}"'

    def run(
        self,
        command: str = '',
        pre_command: str = '',
        post_command: str = '',
        interactive: bool = False,
        cwd: files.Path = '',
        environ: dict = {},
        shell: str = 'bash',
        yes: bool = False,
        dry_run: bool = False,
    ):
        if env.BSUB:
            shell_type = env.Shell.TCSH
        else:
            shell_type = env.Shell(shell)
        shell = shell_type.value

        lines = (
            env.dict_into_environ(environ, shell)
            + [pre_command]
            + [self.build(command, interactive)]
            + [post_command]
        )
        sh = io.StringIO()
        sh.write('\n'.join(filter(lambda x: len(x), lines)))
        sh_text = sh.getvalue()

        if dry_run:
            print(sh_text)
            return sh_text
        else:
            with tempfile.NamedTemporaryFile(
                    mode='w', suffix='.sh', delete=False) as f:
                f.write(sh_text)
                filename = f.name
            print('******************')
            print(sh_text)
            print('******************')
            action = input('Run the command? [Y/n] ').upper()
            if action != 'N' or yes:
                if env.is_batching_system():
                    proc = env.subprocess_run([shell, filename], text=True, cwd=cwd)
                    return proc.stdout or proc.stderr
                else:
                    proc = env.subprocess_popen([shell, filename], cwd=cwd)
                    proc.wait()
                    return proc
            else:
                print(f'{shell} {filename}')


if __name__ == "__main__":
    environ = {'PYTHONPATH': '../src/'}
    cmd = Command('python main.py', arg_style='--')
    cmd.args = {'fast': True, 'worker': 20}
    bsub = BsubCommand({'app': 'pytorch', 'm': '"GPU_HOST"'}, log=True)
    bsub.run(cmd.build(), environ=environ, dry_run=True)
