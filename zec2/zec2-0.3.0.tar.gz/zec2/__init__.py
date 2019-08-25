import click
from click import UsageError
from botocore import exceptions
from terminaltables import AsciiTable

from zec2.aws_ec2 import AwsEc2, AwsVpc


def list_instances(vpcs, ec2):
    i = 0
    tables = []
    for vpc in vpcs.list():
        instances = ec2.list(_filter=[('vpc-id', vpc.id)])
        table_data, i = instance_table_maker(instances, i=i)
        table = AsciiTable(table_data)
        tables.append((vpc.id, table.table))

    for vpc, table in tables:
        click.echo()
        click.secho(vpc, fg='yellow')
        click.echo(table)

    click.echo()


def instance_table_maker(instances, table_data=None, i=None):
    if type(instances) is not list:
        instances = [instances]

    if table_data is None:
        table_data = [
            ['', 'Name', 'Instance ID', 'Private IP', 'Public IP',
             'State', 'Key Pair', 'Type', 'Launch time', 'Zone'],
        ]

    if i is None:
        i = 0

    for instance in instances:
        row = list()

        row.append(str(i + 1))
        row.append(click.style(instance.name(), fg='yellow'))
        row.append(instance.aws.id)
        row.append(instance.aws.private_ip_address)
        row.append(instance.public_ip_address())
        state, state_fg = instance.state()
        row.append(click.style(state, fg=state_fg))
        row.append(instance.aws.key_name)
        row.append(instance.aws.instance_type)
        row.append(instance.aws.launch_time)
        row.append(instance.zone())

        table_data.append(row)

        i += 1

    return table_data, i


def get_aws_objects(aws_profile):
    ec2 = AwsEc2()
    vpcs = AwsVpc()

    if aws_profile:
        ec2.aws_profile(aws_profile)
        vpcs.aws_profile(aws_profile)

    return ec2, vpcs


def get_instance_by_number(number, ec2, vpcs):
    instances = list()
    for vpc in vpcs.list():
        instances += ec2.list(_filter=[('vpc-id', vpc.id)])

    try:
        instance = instances[int(number) - 1]
    except IndexError:
        raise UsageError('There is no instance on number %s' % number)

    return instance


def run_action(number, method, ec2, vpcs):
    instance = get_instance_by_number(number, ec2, vpcs)

    click.echo()
    table_data, i = instance_table_maker(instance)
    table = AsciiTable(table_data)
    click.echo(table.table)
    click.echo()

    instance_id = click.prompt('For safety reason, please enter instance ID: ', type=str)

    if instance.aws.id == instance_id:
        if click.confirm('Do you really want to %s that poor instance?' % method):
            try:
                getattr(instance, method)()
            except exceptions.ClientError:
                if method == 'terminate':
                    if click.confirm(click.style('Termination protection is enabled. \
Do you want to disable it?', fg='red')):
                        instance.disable_api_termination()
                        run_action(number, method, ec2, vpcs)
                else:
                    raise UsageError(str(e))
            except Exception as e:
                raise UsageError(str(e))
    else:
        raise UsageError('Wrong instance ID!')