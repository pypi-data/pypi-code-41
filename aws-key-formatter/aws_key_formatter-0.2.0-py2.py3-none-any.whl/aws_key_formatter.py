# -*- coding: utf-8 -*-

"""Main module."""

import argparse
import textwrap

import boto3


def _format_redshift_credentials(creds, include_token: bool) -> str:
    formatted_str = textwrap.dedent(
        f"""\
        ACCESS_KEY_ID '{creds.access_key}'
        SECRET_ACCESS_KEY '{creds.secret_key}'
        {f"SESSION_TOKEN '{creds.token}'" if include_token else ""}
        """
    ).strip()

    return formatted_str


def _format_env_credentials(creds, include_token: bool) -> str:
    formatted_str = textwrap.dedent(
        f"""\
        AWS_ACCESS_KEY_ID={creds.access_key}
        AWS_SECRET_ACCESS_KEY={creds.secret_key}
        {f"AWS_SESSION_TOKEN={creds.token}" if include_token else ""}
        """
    ).strip()

    return formatted_str


def _get_credentials_for_profile(aws_profile: str):
    session = boto3.Session(profile_name=aws_profile)
    return _get_creds_from_session(session)


def _get_creds_from_session(session):
    return session.get_credentials().get_frozen_credentials()


def main(formatter_type: str, aws_profile: str, include_token: bool):
    creds = _get_credentials_for_profile(aws_profile)
    formatters = {
        "redshift": _format_redshift_credentials,
        "env": _format_env_credentials,
    }

    formatter = formatters.get(formatter_type)
    return formatter(creds, include_token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile", "-p", default="default", help="AWS CLI Profile name"
    )
    parser.add_argument(
        "--include_token", "-t", action="store_true", help="Include AWS Session Token?"
    )

    args = parser.parse_args()

    main(args.profile, args.include_token)
