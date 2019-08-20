# coding: utf-8
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.

from __future__ import print_function
import click
import oci  # noqa: F401
import six  # noqa: F401
import sys  # noqa: F401
from oci_cli import cli_constants  # noqa: F401
from oci_cli import cli_util
from oci_cli import json_skeleton_utils
from oci_cli import custom_types  # noqa: F401
from oci_cli.aliasing import CommandGroupWithAlias
from services.streaming.src.oci_cli_streaming.generated import streaming_service_cli


@click.command(cli_util.override('stream_admin_root_group.command_name', 'stream-admin'), cls=CommandGroupWithAlias, help=cli_util.override('stream_admin_root_group.help', """The API for the Streaming Service."""), short_help=cli_util.override('stream_admin_root_group.short_help', """Streaming Service API"""))
@cli_util.help_option_group
def stream_admin_root_group():
    pass


@click.command(cli_util.override('archiver_group.command_name', 'archiver'), cls=CommandGroupWithAlias, help="""Represents the current state of the stream archiver.""")
@cli_util.help_option_group
def archiver_group():
    pass


@click.command(cli_util.override('stream_group.command_name', 'stream'), cls=CommandGroupWithAlias, help="""Detailed representation of a stream, including all its partitions.""")
@cli_util.help_option_group
def stream_group():
    pass


streaming_service_cli.streaming_service_group.add_command(stream_admin_root_group)
stream_admin_root_group.add_command(archiver_group)
stream_admin_root_group.add_command(stream_group)


@stream_group.command(name=cli_util.override('change_stream_compartment.command_name', 'change-compartment'), help=u"""Moves a resource into a different compartment. When provided, If-Match is checked against ETag values of the resource.""")
@cli_util.option('--stream-id', required=True, help=u"""The OCID of the stream to change compatment for.""")
@cli_util.option('--compartment-id', required=True, help=u"""The [OCID] of the compartment into which the resource should be moved.""")
@cli_util.option('--if-match', help=u"""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the if-match parameter to the value of the etag from a previous GET or POST response for that resource. The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@json_skeleton_utils.get_cli_json_input_option({})
@cli_util.help_option
@click.pass_context
@json_skeleton_utils.json_skeleton_generation_handler(input_params_to_complex_types={})
@cli_util.wrap_exceptions
def change_stream_compartment(ctx, from_json, stream_id, compartment_id, if_match):

    if isinstance(stream_id, six.string_types) and len(stream_id.strip()) == 0:
        raise click.UsageError('Parameter --stream-id cannot be whitespace or empty string')

    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    kwargs['opc_request_id'] = cli_util.use_or_generate_request_id(ctx.obj['request_id'])

    details = {}
    details['compartmentId'] = compartment_id

    client = cli_util.build_client('stream_admin', ctx)
    result = client.change_stream_compartment(
        stream_id=stream_id,
        change_stream_compartment_details=details,
        **kwargs
    )
    cli_util.render_response(result, ctx)


@archiver_group.command(name=cli_util.override('create_archiver.command_name', 'create'), help=u"""Starts the provisioning of a new stream archiver. To track the progress of the provisioning, you can periodically call [GetArchiver]. In the response, the `lifecycleState` parameter of the [Stream] object tells you its current state.""")
@cli_util.option('--stream-id', required=True, help=u"""The OCID of the stream.""")
@cli_util.option('--bucket-name', required=True, help=u"""The name of the bucket.""")
@cli_util.option('--use-existing-bucket', required=True, type=click.BOOL, help=u"""The flag to create a new bucket or use existing one.""")
@cli_util.option('--start-position', required=True, type=custom_types.CliCaseInsensitiveChoice(["LATEST", "TRIM_HORIZON"]), help=u"""The start message.""")
@cli_util.option('--batch-rollover-size-in-mbs', required=True, type=click.INT, help=u"""The batch rollover size in megabytes.""")
@cli_util.option('--batch-rollover-time-in-seconds', required=True, type=click.INT, help=u"""The rollover time in seconds.""")
@cli_util.option('--wait-for-state', type=custom_types.CliCaseInsensitiveChoice(["CREATING", "STOPPED", "STARTING", "RUNNING", "STOPPING", "UPDATING"]), help="""This operation creates, modifies or deletes a resource that has a defined lifecycle state. Specify this option to perform the action and then wait until the resource reaches a given lifecycle state. If timeout is reached, a return code of 2 is returned. For any other error, a return code of 1 is returned.""")
@cli_util.option('--max-wait-seconds', type=click.INT, help="""The maximum time to wait for the resource to reach the lifecycle state defined by --wait-for-state. Defaults to 1200 seconds.""")
@cli_util.option('--wait-interval-seconds', type=click.INT, help="""Check every --wait-interval-seconds to see whether the resource to see if it has reached the lifecycle state defined by --wait-for-state. Defaults to 30 seconds.""")
@json_skeleton_utils.get_cli_json_input_option({})
@cli_util.help_option
@click.pass_context
@json_skeleton_utils.json_skeleton_generation_handler(input_params_to_complex_types={}, output_type={'module': 'streaming', 'class': 'Archiver'})
@cli_util.wrap_exceptions
def create_archiver(ctx, from_json, wait_for_state, max_wait_seconds, wait_interval_seconds, stream_id, bucket_name, use_existing_bucket, start_position, batch_rollover_size_in_mbs, batch_rollover_time_in_seconds):

    if isinstance(stream_id, six.string_types) and len(stream_id.strip()) == 0:
        raise click.UsageError('Parameter --stream-id cannot be whitespace or empty string')

    kwargs = {}
    kwargs['opc_request_id'] = cli_util.use_or_generate_request_id(ctx.obj['request_id'])

    details = {}
    details['bucketName'] = bucket_name
    details['useExistingBucket'] = use_existing_bucket
    details['startPosition'] = start_position
    details['batchRolloverSizeInMBs'] = batch_rollover_size_in_mbs
    details['batchRolloverTimeInSeconds'] = batch_rollover_time_in_seconds

    client = cli_util.build_client('stream_admin', ctx)
    result = client.create_archiver(
        stream_id=stream_id,
        create_archiver_details=details,
        **kwargs
    )
    if wait_for_state:
        if hasattr(client, 'get_archiver') and callable(getattr(client, 'get_archiver')):
            try:
                wait_period_kwargs = {}
                if max_wait_seconds is not None:
                    wait_period_kwargs['max_wait_seconds'] = max_wait_seconds
                if wait_interval_seconds is not None:
                    wait_period_kwargs['max_interval_seconds'] = wait_interval_seconds

                click.echo('Action completed. Waiting until the resource has entered state: {}'.format(wait_for_state), file=sys.stderr)
                result = oci.wait_until(client, client.get_archiver(result.data.id), 'lifecycle_state', wait_for_state, **wait_period_kwargs)
            except oci.exceptions.MaximumWaitTimeExceeded as e:
                # If we fail, we should show an error, but we should still provide the information to the customer
                click.echo('Failed to wait until the resource entered the specified state. Outputting last known resource state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                sys.exit(2)
            except Exception:
                click.echo('Encountered error while waiting for resource to enter the specified state. Outputting last known resource state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                raise
        else:
            click.echo('Unable to wait for the resource to enter the specified state', file=sys.stderr)
    cli_util.render_response(result, ctx)


@stream_group.command(name=cli_util.override('create_stream.command_name', 'create'), help=u"""Starts the provisioning of a new stream. To track the progress of the provisioning, you can periodically call [GetStream]. In the response, the `lifecycleState` parameter of the [Stream] object tells you its current state.""")
@cli_util.option('--name', required=True, help=u"""The name of the stream. Avoid entering confidential information.

Example: `TelemetryEvents`""")
@cli_util.option('--partitions', required=True, type=click.INT, help=u"""The number of partitions in the stream.""")
@cli_util.option('--compartment-id', required=True, help=u"""The OCID of the compartment that contains the stream.""")
@cli_util.option('--retention-in-hours', type=click.INT, help=u"""The retention period of the stream, in hours. Accepted values are between 24 and 168 (7 days). If not specified, the stream will have a retention period of 24 hours.""")
@cli_util.option('--freeform-tags', type=custom_types.CLI_COMPLEX_TYPE, help=u"""Free-form tags for this resource. Each tag is a simple key-value pair that is applied with no predefined name, type, or namespace. Exists for cross-compatibility only. For more information, see [Resource Tags].

Example: `{\"Department\": \"Finance\"}`""" + custom_types.cli_complex_type.COMPLEX_TYPE_HELP)
@cli_util.option('--defined-tags', type=custom_types.CLI_COMPLEX_TYPE, help=u"""Defined tags for this resource. Each key is predefined and scoped to a namespace. For more information, see [Resource Tags].

Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`""" + custom_types.cli_complex_type.COMPLEX_TYPE_HELP)
@cli_util.option('--wait-for-state', type=custom_types.CliCaseInsensitiveChoice(["CREATING", "ACTIVE", "DELETING", "DELETED", "FAILED"]), help="""This operation creates, modifies or deletes a resource that has a defined lifecycle state. Specify this option to perform the action and then wait until the resource reaches a given lifecycle state. If timeout is reached, a return code of 2 is returned. For any other error, a return code of 1 is returned.""")
@cli_util.option('--max-wait-seconds', type=click.INT, help="""The maximum time to wait for the resource to reach the lifecycle state defined by --wait-for-state. Defaults to 1200 seconds.""")
@cli_util.option('--wait-interval-seconds', type=click.INT, help="""Check every --wait-interval-seconds to see whether the resource to see if it has reached the lifecycle state defined by --wait-for-state. Defaults to 30 seconds.""")
@json_skeleton_utils.get_cli_json_input_option({'freeform-tags': {'module': 'streaming', 'class': 'dict(str, string)'}, 'defined-tags': {'module': 'streaming', 'class': 'dict(str, dict(str, object))'}})
@cli_util.help_option
@click.pass_context
@json_skeleton_utils.json_skeleton_generation_handler(input_params_to_complex_types={'freeform-tags': {'module': 'streaming', 'class': 'dict(str, string)'}, 'defined-tags': {'module': 'streaming', 'class': 'dict(str, dict(str, object))'}}, output_type={'module': 'streaming', 'class': 'Stream'})
@cli_util.wrap_exceptions
def create_stream(ctx, from_json, wait_for_state, max_wait_seconds, wait_interval_seconds, name, partitions, compartment_id, retention_in_hours, freeform_tags, defined_tags):

    kwargs = {}
    kwargs['opc_request_id'] = cli_util.use_or_generate_request_id(ctx.obj['request_id'])

    details = {}
    details['name'] = name
    details['partitions'] = partitions
    details['compartmentId'] = compartment_id

    if retention_in_hours is not None:
        details['retentionInHours'] = retention_in_hours

    if freeform_tags is not None:
        details['freeformTags'] = cli_util.parse_json_parameter("freeform_tags", freeform_tags)

    if defined_tags is not None:
        details['definedTags'] = cli_util.parse_json_parameter("defined_tags", defined_tags)

    client = cli_util.build_client('stream_admin', ctx)
    result = client.create_stream(
        create_stream_details=details,
        **kwargs
    )
    if wait_for_state:
        if hasattr(client, 'get_stream') and callable(getattr(client, 'get_stream')):
            try:
                wait_period_kwargs = {}
                if max_wait_seconds is not None:
                    wait_period_kwargs['max_wait_seconds'] = max_wait_seconds
                if wait_interval_seconds is not None:
                    wait_period_kwargs['max_interval_seconds'] = wait_interval_seconds

                click.echo('Action completed. Waiting until the resource has entered state: {}'.format(wait_for_state), file=sys.stderr)
                result = oci.wait_until(client, client.get_stream(result.data.id), 'lifecycle_state', wait_for_state, **wait_period_kwargs)
            except oci.exceptions.MaximumWaitTimeExceeded as e:
                # If we fail, we should show an error, but we should still provide the information to the customer
                click.echo('Failed to wait until the resource entered the specified state. Outputting last known resource state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                sys.exit(2)
            except Exception:
                click.echo('Encountered error while waiting for resource to enter the specified state. Outputting last known resource state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                raise
        else:
            click.echo('Unable to wait for the resource to enter the specified state', file=sys.stderr)
    cli_util.render_response(result, ctx)


@stream_group.command(name=cli_util.override('delete_stream.command_name', 'delete'), help=u"""Deletes a stream and its content. Stream contents are deleted immediately. The service retains records of the stream itself for 90 days after deletion. The `lifecycleState` parameter of the `Stream` object changes to `DELETING` and the stream becomes inaccessible for read or write operations. To verify that a stream has been deleted, make a [GetStream] request. If the call returns the stream's lifecycle state as `DELETED`, then the stream has been deleted. If the call returns a \"404 Not Found\" error, that means all records of the stream have been deleted.""")
@cli_util.option('--stream-id', required=True, help=u"""The OCID of the stream to delete.""")
@cli_util.option('--if-match', help=u"""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the if-match parameter to the value of the etag from a previous GET or POST response for that resource. The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.confirm_delete_option
@cli_util.option('--wait-for-state', type=custom_types.CliCaseInsensitiveChoice(["CREATING", "ACTIVE", "DELETING", "DELETED", "FAILED"]), help="""This operation creates, modifies or deletes a resource that has a defined lifecycle state. Specify this option to perform the action and then wait until the resource reaches a given lifecycle state. If timeout is reached, a return code of 2 is returned. For any other error, a return code of 1 is returned.""")
@cli_util.option('--max-wait-seconds', type=click.INT, help="""The maximum time to wait for the resource to reach the lifecycle state defined by --wait-for-state. Defaults to 1200 seconds.""")
@cli_util.option('--wait-interval-seconds', type=click.INT, help="""Check every --wait-interval-seconds to see whether the resource to see if it has reached the lifecycle state defined by --wait-for-state. Defaults to 30 seconds.""")
@json_skeleton_utils.get_cli_json_input_option({})
@cli_util.help_option
@click.pass_context
@json_skeleton_utils.json_skeleton_generation_handler(input_params_to_complex_types={})
@cli_util.wrap_exceptions
def delete_stream(ctx, from_json, wait_for_state, max_wait_seconds, wait_interval_seconds, stream_id, if_match):

    if isinstance(stream_id, six.string_types) and len(stream_id.strip()) == 0:
        raise click.UsageError('Parameter --stream-id cannot be whitespace or empty string')

    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    kwargs['opc_request_id'] = cli_util.use_or_generate_request_id(ctx.obj['request_id'])
    client = cli_util.build_client('stream_admin', ctx)
    result = client.delete_stream(
        stream_id=stream_id,
        **kwargs
    )
    if wait_for_state:
        if hasattr(client, 'get_stream') and callable(getattr(client, 'get_stream')):
            try:
                wait_period_kwargs = {}
                if max_wait_seconds is not None:
                    wait_period_kwargs['max_wait_seconds'] = max_wait_seconds
                if wait_interval_seconds is not None:
                    wait_period_kwargs['max_interval_seconds'] = wait_interval_seconds

                click.echo('Action completed. Waiting until the resource has entered state: {}'.format(wait_for_state), file=sys.stderr)
                oci.wait_until(client, client.get_stream(stream_id), 'lifecycle_state', wait_for_state, succeed_on_not_found=True, **wait_period_kwargs)
            except oci.exceptions.ServiceError as e:
                # We make an initial service call so we can pass the result to oci.wait_until(), however if we are waiting on the
                # outcome of a delete operation it is possible that the resource is already gone and so the initial service call
                # will result in an exception that reflects a HTTP 404. In this case, we can exit with success (rather than raising
                # the exception) since this would have been the behaviour in the waiter anyway (as for delete we provide the argument
                # succeed_on_not_found=True to the waiter).
                #
                # Any non-404 should still result in the exception being thrown.
                if e.status == 404:
                    pass
                else:
                    raise
            except oci.exceptions.MaximumWaitTimeExceeded as e:
                # If we fail, we should show an error, but we should still provide the information to the customer
                click.echo('Failed to wait until the resource entered the specified state. Please retrieve the resource to find its current state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                sys.exit(2)
            except Exception:
                click.echo('Encountered error while waiting for resource to enter the specified state. Outputting last known resource state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                raise
        else:
            click.echo('Unable to wait for the resource to enter the specified state', file=sys.stderr)
    cli_util.render_response(result, ctx)


@archiver_group.command(name=cli_util.override('get_archiver.command_name', 'get'), help=u"""Returns the current state of the stream archiver.""")
@cli_util.option('--stream-id', required=True, help=u"""The OCID of the stream.""")
@json_skeleton_utils.get_cli_json_input_option({})
@cli_util.help_option
@click.pass_context
@json_skeleton_utils.json_skeleton_generation_handler(input_params_to_complex_types={}, output_type={'module': 'streaming', 'class': 'Archiver'})
@cli_util.wrap_exceptions
def get_archiver(ctx, from_json, stream_id):

    if isinstance(stream_id, six.string_types) and len(stream_id.strip()) == 0:
        raise click.UsageError('Parameter --stream-id cannot be whitespace or empty string')

    kwargs = {}
    kwargs['opc_request_id'] = cli_util.use_or_generate_request_id(ctx.obj['request_id'])
    client = cli_util.build_client('stream_admin', ctx)
    result = client.get_archiver(
        stream_id=stream_id,
        **kwargs
    )
    cli_util.render_response(result, ctx)


@stream_group.command(name=cli_util.override('get_stream.command_name', 'get'), help=u"""Gets detailed information about a stream, including the number of partitions.""")
@cli_util.option('--stream-id', required=True, help=u"""The OCID of the stream to retrieve.""")
@json_skeleton_utils.get_cli_json_input_option({})
@cli_util.help_option
@click.pass_context
@json_skeleton_utils.json_skeleton_generation_handler(input_params_to_complex_types={}, output_type={'module': 'streaming', 'class': 'Stream'})
@cli_util.wrap_exceptions
def get_stream(ctx, from_json, stream_id):

    if isinstance(stream_id, six.string_types) and len(stream_id.strip()) == 0:
        raise click.UsageError('Parameter --stream-id cannot be whitespace or empty string')

    kwargs = {}
    kwargs['opc_request_id'] = cli_util.use_or_generate_request_id(ctx.obj['request_id'])
    client = cli_util.build_client('stream_admin', ctx)
    result = client.get_stream(
        stream_id=stream_id,
        **kwargs
    )
    cli_util.render_response(result, ctx)


@stream_group.command(name=cli_util.override('list_streams.command_name', 'list'), help=u"""Lists the streams.""")
@cli_util.option('--compartment-id', required=True, help=u"""The OCID of the compartment.""")
@cli_util.option('--id', help=u"""A filter to return only resources that match the given ID exactly.""")
@cli_util.option('--name', help=u"""A filter to return only resources that match the given name exactly.""")
@cli_util.option('--limit', type=click.INT, help=u"""The maximum number of items to return. The value must be between 1 and 50. The default is 10.""")
@cli_util.option('--page', help=u"""The page at which to start retrieving results.""")
@cli_util.option('--sort-by', type=custom_types.CliCaseInsensitiveChoice(["NAME", "TIMECREATED"]), help=u"""The field to sort by. You can provide no more than one sort order. By default, `TIMECREATED` sorts results in descending order and `NAME` sorts results in ascending order.""")
@cli_util.option('--sort-order', type=custom_types.CliCaseInsensitiveChoice(["ASC", "DESC"]), help=u"""The sort order to use, either 'asc' or 'desc'.""")
@cli_util.option('--lifecycle-state', type=custom_types.CliCaseInsensitiveChoice(["CREATING", "ACTIVE", "DELETING", "DELETED", "FAILED"]), help=u"""A filter to only return resources that match the given lifecycle state. The state value is case-insensitive.""")
@cli_util.option('--all', 'all_pages', is_flag=True, help="""Fetches all pages of results. If you provide this option, then you cannot provide the --limit option.""")
@cli_util.option('--page-size', type=click.INT, help="""When fetching results, the number of results to fetch per call. Only valid when used with --all or --limit, and ignored otherwise.""")
@json_skeleton_utils.get_cli_json_input_option({})
@cli_util.help_option
@click.pass_context
@json_skeleton_utils.json_skeleton_generation_handler(input_params_to_complex_types={}, output_type={'module': 'streaming', 'class': 'list[StreamSummary]'})
@cli_util.wrap_exceptions
def list_streams(ctx, from_json, all_pages, page_size, compartment_id, id, name, limit, page, sort_by, sort_order, lifecycle_state):

    if all_pages and limit:
        raise click.UsageError('If you provide the --all option you cannot provide the --limit option')

    kwargs = {}
    if id is not None:
        kwargs['id'] = id
    if name is not None:
        kwargs['name'] = name
    if limit is not None:
        kwargs['limit'] = limit
    if page is not None:
        kwargs['page'] = page
    if sort_by is not None:
        kwargs['sort_by'] = sort_by
    if sort_order is not None:
        kwargs['sort_order'] = sort_order
    if lifecycle_state is not None:
        kwargs['lifecycle_state'] = lifecycle_state
    kwargs['opc_request_id'] = cli_util.use_or_generate_request_id(ctx.obj['request_id'])
    client = cli_util.build_client('stream_admin', ctx)
    if all_pages:
        if page_size:
            kwargs['limit'] = page_size

        result = cli_util.list_call_get_all_results(
            client.list_streams,
            compartment_id=compartment_id,
            **kwargs
        )
    elif limit is not None:
        result = cli_util.list_call_get_up_to_limit(
            client.list_streams,
            limit,
            page_size,
            compartment_id=compartment_id,
            **kwargs
        )
    else:
        result = client.list_streams(
            compartment_id=compartment_id,
            **kwargs
        )
    cli_util.render_response(result, ctx)


@archiver_group.command(name=cli_util.override('start_archiver.command_name', 'start'), help=u"""Start the archiver for the specified stream.""")
@cli_util.option('--stream-id', required=True, help=u"""The OCID of the stream.""")
@cli_util.option('--if-match', help=u"""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the if-match parameter to the value of the etag from a previous GET or POST response for that resource. The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.option('--wait-for-state', type=custom_types.CliCaseInsensitiveChoice(["CREATING", "STOPPED", "STARTING", "RUNNING", "STOPPING", "UPDATING"]), help="""This operation creates, modifies or deletes a resource that has a defined lifecycle state. Specify this option to perform the action and then wait until the resource reaches a given lifecycle state. If timeout is reached, a return code of 2 is returned. For any other error, a return code of 1 is returned.""")
@cli_util.option('--max-wait-seconds', type=click.INT, help="""The maximum time to wait for the resource to reach the lifecycle state defined by --wait-for-state. Defaults to 1200 seconds.""")
@cli_util.option('--wait-interval-seconds', type=click.INT, help="""Check every --wait-interval-seconds to see whether the resource to see if it has reached the lifecycle state defined by --wait-for-state. Defaults to 30 seconds.""")
@json_skeleton_utils.get_cli_json_input_option({})
@cli_util.help_option
@click.pass_context
@json_skeleton_utils.json_skeleton_generation_handler(input_params_to_complex_types={}, output_type={'module': 'streaming', 'class': 'Archiver'})
@cli_util.wrap_exceptions
def start_archiver(ctx, from_json, wait_for_state, max_wait_seconds, wait_interval_seconds, stream_id, if_match):

    if isinstance(stream_id, six.string_types) and len(stream_id.strip()) == 0:
        raise click.UsageError('Parameter --stream-id cannot be whitespace or empty string')

    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    kwargs['opc_request_id'] = cli_util.use_or_generate_request_id(ctx.obj['request_id'])
    client = cli_util.build_client('stream_admin', ctx)
    result = client.start_archiver(
        stream_id=stream_id,
        **kwargs
    )
    if wait_for_state:
        if hasattr(client, 'get_archiver') and callable(getattr(client, 'get_archiver')):
            try:
                wait_period_kwargs = {}
                if max_wait_seconds is not None:
                    wait_period_kwargs['max_wait_seconds'] = max_wait_seconds
                if wait_interval_seconds is not None:
                    wait_period_kwargs['max_interval_seconds'] = wait_interval_seconds

                click.echo('Action completed. Waiting until the resource has entered state: {}'.format(wait_for_state), file=sys.stderr)
                result = oci.wait_until(client, client.get_archiver(result.data.id), 'lifecycle_state', wait_for_state, **wait_period_kwargs)
            except oci.exceptions.MaximumWaitTimeExceeded as e:
                # If we fail, we should show an error, but we should still provide the information to the customer
                click.echo('Failed to wait until the resource entered the specified state. Outputting last known resource state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                sys.exit(2)
            except Exception:
                click.echo('Encountered error while waiting for resource to enter the specified state. Outputting last known resource state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                raise
        else:
            click.echo('Unable to wait for the resource to enter the specified state', file=sys.stderr)
    cli_util.render_response(result, ctx)


@archiver_group.command(name=cli_util.override('stop_archiver.command_name', 'stop'), help=u"""Stop the archiver for the specified stream.""")
@cli_util.option('--stream-id', required=True, help=u"""The OCID of the stream.""")
@cli_util.option('--if-match', help=u"""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the if-match parameter to the value of the etag from a previous GET or POST response for that resource. The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.option('--wait-for-state', type=custom_types.CliCaseInsensitiveChoice(["CREATING", "STOPPED", "STARTING", "RUNNING", "STOPPING", "UPDATING"]), help="""This operation creates, modifies or deletes a resource that has a defined lifecycle state. Specify this option to perform the action and then wait until the resource reaches a given lifecycle state. If timeout is reached, a return code of 2 is returned. For any other error, a return code of 1 is returned.""")
@cli_util.option('--max-wait-seconds', type=click.INT, help="""The maximum time to wait for the resource to reach the lifecycle state defined by --wait-for-state. Defaults to 1200 seconds.""")
@cli_util.option('--wait-interval-seconds', type=click.INT, help="""Check every --wait-interval-seconds to see whether the resource to see if it has reached the lifecycle state defined by --wait-for-state. Defaults to 30 seconds.""")
@json_skeleton_utils.get_cli_json_input_option({})
@cli_util.help_option
@click.pass_context
@json_skeleton_utils.json_skeleton_generation_handler(input_params_to_complex_types={}, output_type={'module': 'streaming', 'class': 'Archiver'})
@cli_util.wrap_exceptions
def stop_archiver(ctx, from_json, wait_for_state, max_wait_seconds, wait_interval_seconds, stream_id, if_match):

    if isinstance(stream_id, six.string_types) and len(stream_id.strip()) == 0:
        raise click.UsageError('Parameter --stream-id cannot be whitespace or empty string')

    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    kwargs['opc_request_id'] = cli_util.use_or_generate_request_id(ctx.obj['request_id'])
    client = cli_util.build_client('stream_admin', ctx)
    result = client.stop_archiver(
        stream_id=stream_id,
        **kwargs
    )
    if wait_for_state:
        if hasattr(client, 'get_archiver') and callable(getattr(client, 'get_archiver')):
            try:
                wait_period_kwargs = {}
                if max_wait_seconds is not None:
                    wait_period_kwargs['max_wait_seconds'] = max_wait_seconds
                if wait_interval_seconds is not None:
                    wait_period_kwargs['max_interval_seconds'] = wait_interval_seconds

                click.echo('Action completed. Waiting until the resource has entered state: {}'.format(wait_for_state), file=sys.stderr)
                result = oci.wait_until(client, client.get_archiver(result.data.id), 'lifecycle_state', wait_for_state, **wait_period_kwargs)
            except oci.exceptions.MaximumWaitTimeExceeded as e:
                # If we fail, we should show an error, but we should still provide the information to the customer
                click.echo('Failed to wait until the resource entered the specified state. Outputting last known resource state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                sys.exit(2)
            except Exception:
                click.echo('Encountered error while waiting for resource to enter the specified state. Outputting last known resource state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                raise
        else:
            click.echo('Unable to wait for the resource to enter the specified state', file=sys.stderr)
    cli_util.render_response(result, ctx)


@archiver_group.command(name=cli_util.override('update_archiver.command_name', 'update'), help=u"""Update the stream archiver parameters.""")
@cli_util.option('--stream-id', required=True, help=u"""The OCID of the stream.""")
@cli_util.option('--bucket-name', help=u"""The name of the bucket.""")
@cli_util.option('--use-existing-bucket', type=click.BOOL, help=u"""The flag to create a new bucket or use existing one.""")
@cli_util.option('--start-position', type=custom_types.CliCaseInsensitiveChoice(["LATEST", "TRIM_HORIZON"]), help=u"""The start message.""")
@cli_util.option('--batch-rollover-size-in-mbs', type=click.INT, help=u"""The batch rollover size in megabytes.""")
@cli_util.option('--batch-rollover-time-in-seconds', type=click.INT, help=u"""The rollover time in seconds.""")
@cli_util.option('--if-match', help=u"""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the if-match parameter to the value of the etag from a previous GET or POST response for that resource. The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.option('--wait-for-state', type=custom_types.CliCaseInsensitiveChoice(["CREATING", "STOPPED", "STARTING", "RUNNING", "STOPPING", "UPDATING"]), help="""This operation creates, modifies or deletes a resource that has a defined lifecycle state. Specify this option to perform the action and then wait until the resource reaches a given lifecycle state. If timeout is reached, a return code of 2 is returned. For any other error, a return code of 1 is returned.""")
@cli_util.option('--max-wait-seconds', type=click.INT, help="""The maximum time to wait for the resource to reach the lifecycle state defined by --wait-for-state. Defaults to 1200 seconds.""")
@cli_util.option('--wait-interval-seconds', type=click.INT, help="""Check every --wait-interval-seconds to see whether the resource to see if it has reached the lifecycle state defined by --wait-for-state. Defaults to 30 seconds.""")
@json_skeleton_utils.get_cli_json_input_option({})
@cli_util.help_option
@click.pass_context
@json_skeleton_utils.json_skeleton_generation_handler(input_params_to_complex_types={}, output_type={'module': 'streaming', 'class': 'Archiver'})
@cli_util.wrap_exceptions
def update_archiver(ctx, from_json, wait_for_state, max_wait_seconds, wait_interval_seconds, stream_id, bucket_name, use_existing_bucket, start_position, batch_rollover_size_in_mbs, batch_rollover_time_in_seconds, if_match):

    if isinstance(stream_id, six.string_types) and len(stream_id.strip()) == 0:
        raise click.UsageError('Parameter --stream-id cannot be whitespace or empty string')

    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    kwargs['opc_request_id'] = cli_util.use_or_generate_request_id(ctx.obj['request_id'])

    details = {}

    if bucket_name is not None:
        details['bucketName'] = bucket_name

    if use_existing_bucket is not None:
        details['useExistingBucket'] = use_existing_bucket

    if start_position is not None:
        details['startPosition'] = start_position

    if batch_rollover_size_in_mbs is not None:
        details['batchRolloverSizeInMBs'] = batch_rollover_size_in_mbs

    if batch_rollover_time_in_seconds is not None:
        details['batchRolloverTimeInSeconds'] = batch_rollover_time_in_seconds

    client = cli_util.build_client('stream_admin', ctx)
    result = client.update_archiver(
        stream_id=stream_id,
        update_archiver_details=details,
        **kwargs
    )
    if wait_for_state:
        if hasattr(client, 'get_archiver') and callable(getattr(client, 'get_archiver')):
            try:
                wait_period_kwargs = {}
                if max_wait_seconds is not None:
                    wait_period_kwargs['max_wait_seconds'] = max_wait_seconds
                if wait_interval_seconds is not None:
                    wait_period_kwargs['max_interval_seconds'] = wait_interval_seconds

                click.echo('Action completed. Waiting until the resource has entered state: {}'.format(wait_for_state), file=sys.stderr)
                result = oci.wait_until(client, client.get_archiver(result.data.id), 'lifecycle_state', wait_for_state, **wait_period_kwargs)
            except oci.exceptions.MaximumWaitTimeExceeded as e:
                # If we fail, we should show an error, but we should still provide the information to the customer
                click.echo('Failed to wait until the resource entered the specified state. Outputting last known resource state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                sys.exit(2)
            except Exception:
                click.echo('Encountered error while waiting for resource to enter the specified state. Outputting last known resource state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                raise
        else:
            click.echo('Unable to wait for the resource to enter the specified state', file=sys.stderr)
    cli_util.render_response(result, ctx)


@stream_group.command(name=cli_util.override('update_stream.command_name', 'update'), help=u"""Updates the tags applied to the stream.""")
@cli_util.option('--stream-id', required=True, help=u"""The OCID of the stream to update.""")
@cli_util.option('--freeform-tags', type=custom_types.CLI_COMPLEX_TYPE, help=u"""Free-form tags for this resource. Each tag is a simple key-value pair that is applied with no predefined name, type, or namespace. Exists for cross-compatibility only. For more information, see [Resource Tags].

Example: `{\"Department\": \"Finance\"}`""" + custom_types.cli_complex_type.COMPLEX_TYPE_HELP)
@cli_util.option('--defined-tags', type=custom_types.CLI_COMPLEX_TYPE, help=u"""Defined tags for this resource. Each key is predefined and scoped to a namespace. For more information, see [Resource Tags].

Example: `{\"Operations\": {\"CostCenter\": \"42\"}}`""" + custom_types.cli_complex_type.COMPLEX_TYPE_HELP)
@cli_util.option('--if-match', help=u"""For optimistic concurrency control. In the PUT or DELETE call for a resource, set the if-match parameter to the value of the etag from a previous GET or POST response for that resource. The resource will be updated or deleted only if the etag you provide matches the resource's current etag value.""")
@cli_util.option('--force', help="""Perform update without prompting for confirmation.""", is_flag=True)
@cli_util.option('--wait-for-state', type=custom_types.CliCaseInsensitiveChoice(["CREATING", "ACTIVE", "DELETING", "DELETED", "FAILED"]), help="""This operation creates, modifies or deletes a resource that has a defined lifecycle state. Specify this option to perform the action and then wait until the resource reaches a given lifecycle state. If timeout is reached, a return code of 2 is returned. For any other error, a return code of 1 is returned.""")
@cli_util.option('--max-wait-seconds', type=click.INT, help="""The maximum time to wait for the resource to reach the lifecycle state defined by --wait-for-state. Defaults to 1200 seconds.""")
@cli_util.option('--wait-interval-seconds', type=click.INT, help="""Check every --wait-interval-seconds to see whether the resource to see if it has reached the lifecycle state defined by --wait-for-state. Defaults to 30 seconds.""")
@json_skeleton_utils.get_cli_json_input_option({'freeform-tags': {'module': 'streaming', 'class': 'dict(str, string)'}, 'defined-tags': {'module': 'streaming', 'class': 'dict(str, dict(str, object))'}})
@cli_util.help_option
@click.pass_context
@json_skeleton_utils.json_skeleton_generation_handler(input_params_to_complex_types={'freeform-tags': {'module': 'streaming', 'class': 'dict(str, string)'}, 'defined-tags': {'module': 'streaming', 'class': 'dict(str, dict(str, object))'}}, output_type={'module': 'streaming', 'class': 'Stream'})
@cli_util.wrap_exceptions
def update_stream(ctx, from_json, force, wait_for_state, max_wait_seconds, wait_interval_seconds, stream_id, freeform_tags, defined_tags, if_match):

    if isinstance(stream_id, six.string_types) and len(stream_id.strip()) == 0:
        raise click.UsageError('Parameter --stream-id cannot be whitespace or empty string')
    if not force:
        if freeform_tags or defined_tags:
            if not click.confirm("WARNING: Updates to freeform-tags and defined-tags will replace any existing values. Are you sure you want to continue?"):
                ctx.abort()

    kwargs = {}
    if if_match is not None:
        kwargs['if_match'] = if_match
    kwargs['opc_request_id'] = cli_util.use_or_generate_request_id(ctx.obj['request_id'])

    details = {}

    if freeform_tags is not None:
        details['freeformTags'] = cli_util.parse_json_parameter("freeform_tags", freeform_tags)

    if defined_tags is not None:
        details['definedTags'] = cli_util.parse_json_parameter("defined_tags", defined_tags)

    client = cli_util.build_client('stream_admin', ctx)
    result = client.update_stream(
        stream_id=stream_id,
        update_stream_details=details,
        **kwargs
    )
    if wait_for_state:
        if hasattr(client, 'get_stream') and callable(getattr(client, 'get_stream')):
            try:
                wait_period_kwargs = {}
                if max_wait_seconds is not None:
                    wait_period_kwargs['max_wait_seconds'] = max_wait_seconds
                if wait_interval_seconds is not None:
                    wait_period_kwargs['max_interval_seconds'] = wait_interval_seconds

                click.echo('Action completed. Waiting until the resource has entered state: {}'.format(wait_for_state), file=sys.stderr)
                result = oci.wait_until(client, client.get_stream(result.data.id), 'lifecycle_state', wait_for_state, **wait_period_kwargs)
            except oci.exceptions.MaximumWaitTimeExceeded as e:
                # If we fail, we should show an error, but we should still provide the information to the customer
                click.echo('Failed to wait until the resource entered the specified state. Outputting last known resource state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                sys.exit(2)
            except Exception:
                click.echo('Encountered error while waiting for resource to enter the specified state. Outputting last known resource state', file=sys.stderr)
                cli_util.render_response(result, ctx)
                raise
        else:
            click.echo('Unable to wait for the resource to enter the specified state', file=sys.stderr)
    cli_util.render_response(result, ctx)
