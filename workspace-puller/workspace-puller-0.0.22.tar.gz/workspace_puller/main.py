import argparse

from workspace_puller.workspace_puller import WorkspacePuller


def start():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_url', type=str)
    parser.add_argument('--bot_token', type=str)
    args = parser.parse_args()
    config_url = args.config_url
    token = args.bot_token
    if config_url is not None:
        wp = WorkspacePuller(config_url=config_url, telegram_token=token)
        wp.build_workspace()


if __name__ == "__main__":
    start()
