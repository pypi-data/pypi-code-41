# -*- coding: utf-8 -*-
import click

from missinglink.commands.utilities.options import CommonOptions
from missinglink.commands.cloud.gcp import GcpContext, install_gcp_dependencies
from missinglink.core.context import Expando
from .resources import resources_commands


@resources_commands.group('gcp')
@click.pass_context
def gcp_commands(ctx, **_):
    ctx.obj.gcp = Expando()


@gcp_commands.command('init', help='Initialize Resource Management on Google Cloud,'
                                   'creating the cloud connection and the default queue and resource group.')
@CommonOptions.org_option()
@click.option('--project', envvar='ML_GCP_PROJECT', help='GCP project name to use', required=True)
@click.option('--region', envvar='ML_GCP_REGION', help='GCP region to use', required=False)
@click.option('--zone', envvar='ML_GCP_ZONE', help='GCP zone to use', required=False)
@click.option('--network', envvar='ML_GCP_NETWORK', help='GCP network to use', required=False)
@click.option('--queue', help='Missinglink dedicated queue to use', required=False)
@click.option('--credentials-file-path', help='Path to GCP credentials json', required=False)
@click.pass_context
def init_auth(ctx, **kwargs):
    region = kwargs.pop('region', None)
    zone = kwargs.pop('zone', None)

    GcpContext.validate_region_and_zone(region, zone)
    if not region:
        region = GcpContext.extract_region_from_zone(zone)

    ctx.obj.gcp.project_id = kwargs.pop('project', None)
    ctx.obj.gcp.region = region
    ctx.obj.gcp.zone = zone
    ctx.obj.gcp.network = kwargs.pop('network', None)
    queue = kwargs.get('queue')

    click.echo('(1/9) Installing missing GCP dependencies')
    install_gcp_dependencies()

    gcp_context = GcpContext(ctx, kwargs)

    if queue:
        # This will fail when the group is not present
        gcp_context.get_queue(queue)

    gcp_context.init_and_authorise_app()
