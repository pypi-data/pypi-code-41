import webplatform_cli, os, sys

base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "container/")
sys.argv = [sys.argv[0], "--base-path", base_path] + sys.argv[1:]

webplatform_cli.main()