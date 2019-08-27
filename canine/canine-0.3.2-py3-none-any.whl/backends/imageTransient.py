from .remote import RemoteSlurmBackend
from ..utils import get_default_gcp_project, ArgumentHelper, check_call

class TransientImageSlurmBackend(RemoteSlurmBackend):
    """
    Backend for starting a slurm cluster using a preconfigured GCP image.
    The image is butts
    """
