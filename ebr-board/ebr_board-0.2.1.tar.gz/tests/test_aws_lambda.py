from unittest.mock import patch, Mock
from copy import deepcopy

from ebr_board.aws_lambda import handler


@patch("ebr_board.aws_lambda.awsgi.response")
@patch("ebr_board.aws_lambda.create_app")
@patch("ebr_board.aws_lambda.EC2ParameterStore")
def test_aws_lambda_handler(mock_ec2paramstore, mock_create_app, mock_awsgi_response, monkeypatch):
    """
    Tests that the aws lambda handler correctly processes environ variables and sets up the app correctly
    """
    environ = {
        "config_name": "test_config",
        "vault_config_name": "test_vault_config",
        "vault_creds_name": "test_vault_creds",
        "config_format": "test_format",
    }
    for key, value in environ.items():
        monkeypatch.setenv(key, value)

    mock_ec2paramstore.return_value.get_parameters.return_value = {
        "test_config": "config_data",
        "test_vault_config": "vault_config_data",
        "test_vault_creds": "vault_creds_data",
    }

    handler("test-event", "test-context")

    del environ["config_format"]
    mock_ec2paramstore.return_value.get_parameters.assert_called_with(list(environ.values()), decrypt=True)
    mock_create_app.assert_called_with(
        config="config_data",
        vault_config="vault_config_data",
        vault_creds="vault_creds_data",
        config_format="test_format",
    )
    mock_awsgi_response.assert_called_with(mock_create_app.return_value, "test-event", "test-context")


@patch("ebr_board.aws_lambda.awsgi.response")
@patch("ebr_board.aws_lambda.create_app")
@patch("ebr_board.aws_lambda.EC2ParameterStore")
def test_aws_lambda_handler_default_environment(mock_ec2paramstore, mock_create_app, mock_awsgi_response):
    """
    Tests that the aws lambda handler correctly processes environ variables and sets up the app correctly without environmental variables set
    """
    default_environ = {
        "config_name": "ebr_board_config",
        "vault_config_name": "ebr_board_vault_config",
        "vault_creds_name": "ebr_board_vault_creds",
    }

    mock_ec2paramstore.return_value.get_parameters.return_value = {
        "ebr_board_config": "config_data",
        "ebr_board_vault_config": "vault_config_data",
        "ebr_board_vault_creds": "vault_creds_data",
    }

    handler("test-event", "test-context")

    mock_ec2paramstore.return_value.get_parameters.assert_called_with(list(default_environ.values()), decrypt=True)
    mock_create_app.assert_called_with(
        config="config_data", vault_config="vault_config_data", vault_creds="vault_creds_data", config_format="yaml"
    )
    mock_awsgi_response.assert_called_with(mock_create_app.return_value, "test-event", "test-context")
