import click
from indico_install.helm.apply import apply, apply_patch, info
from indico_install.helm.render import render

# Here we try and include the upload function
# It depends on google-cloud-storage which may not be installed
# in which case we include a stub instead
try:
    from indico_install.helm.upload import upload
except ImportError:
    @click.command("upload")
    def upload():
        """Not available"""
        pass
