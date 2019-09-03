import subprocess
import os


def main():
    script_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_path)
    subprocess.run(['gunicorn', '-c', 'guniconfig.py.ini', 'run:server'])


if __name__ == '__main__':
    main()
