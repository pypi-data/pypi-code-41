"""MetadataClientApi class"""

# Import Oauth2ClientBackend from Oauth2Client class
from oauth2_xfel_client.oauth2_client_backend import Oauth2ClientBackend

# Import Metadata Catalogue Web Application RESTful APIs classes
from .apis.repostory_api import RepositoryApi
from .apis.experiment_type_api import ExperimentTypeApi
from .apis.data_group_repository_api import DataGroupRepositoryApi
from .apis.data_group_type_api import DataGroupTypeApi
from .apis.parameter_type_api import ParameterTypeApi
from .apis.data_type_api import DataTypeApi
from .apis.parameter_api import ParameterApi
from .apis.instrument_api import InstrumentApi
from .apis.proposal_api import ProposalApi
from .apis.sample_api import SampleApi
from .apis.experiment_api import ExperimentApi
from .apis.run_api import RunApi
from .apis.data_group_api import DataGroupApi
from .apis.data_file_api import DataFileApi
from .apis.user_api import UserApi
from .common.config import EMAIL_HEADER, DEF_HEADERS


class MetadataClientApi(ExperimentTypeApi, DataGroupTypeApi, RepositoryApi,
                        ParameterTypeApi, DataTypeApi, ParameterApi,
                        InstrumentApi, ProposalApi,
                        SampleApi, ExperimentApi,
                        RunApi, DataGroupApi, DataFileApi,
                        DataGroupRepositoryApi, UserApi):
    def __init__(self,
                 client_id, client_secret,
                 token_url, refresh_url, auth_url, scope,
                 user_email, base_api_url,
                 session_token=None):
        self.oauth_client = Oauth2ClientBackend(client_id=client_id,
                                                client_secret=client_secret,
                                                scope=scope,
                                                token_url=token_url,
                                                refresh_url=refresh_url,
                                                auth_url=auth_url,
                                                session_token=session_token)

        self.headers = DEF_HEADERS
        self.headers.update({EMAIL_HEADER: user_email})
        self.headers.update(self.oauth_client.headers)

        self.base_api_url = base_api_url
