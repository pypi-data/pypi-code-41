import click
from .control import Control
from .profile import Profile
from .util import timestamp2iso


control = Control()


ctx_pass_through_args = {
	'ignore_unknown_options': True
}


@click.group(context_settings={
	'help_option_names': ('-h', '--help')
})
def cli():
	'''
	dotcontrol is a dot file manager.
	'''


@cli.command('.', help='list dots in a profile.')
@click.option('-p', '--profile', help='specify profile(s) to list, separate with comma withour whitespace.')
@click.option('-a', '--all', is_flag=True, help='list dots in all profiles.')
@click.option('-l', '--detail', is_flag=True, help='also list details about dots.')
def list_dots(profile, all, detail):
	if all:
		profiles = control.iter_profiles()
	else:
		if not profile:
			profiles = (control.current_profile,)
		else:
			profiles = (Profile.get(control, name) for name in profile.split(','))
	for profile in profiles:
		click.secho(profile.name, fg='cyan')
		for dot in profile.iter_dots():
			if dot.changed:
				click.secho('* ', fg='red', nl=False)
			if detail:
				click.secho(timestamp2iso(dot.data['last_sha1_check']), nl=False)
				click.echo(' ', nl=False)
			click.secho(dot.normalized_origin_path, bold=(dot.type =='dir'), nl=not detail)
			if detail:
				click.echo(' ', nl=False)
				if dot.type == 'file':
					click.echo(dot.data['sha1'])
				elif dot.type == 'dir':
					click.echo()
					for k in dot.data['sha1']:
						click.echo('{} {}'.format(dot.data['sha1'][k], k))


@cli.command('+', help='add or update dot(s).')
@click.option('-p', '--profile', help='specify profile to add or update dot(s).')
@click.argument('paths', nargs=-1, required=True)
def set_dots(profile, paths):
	if not profile:
		profile = control.current_profile
	else:
		profile = Profile.get(control, profile)
	
	for path in paths:
		dot = profile.set_dot(path)
		click.echo('added ', nl=False)
		click.secho(dot.normalized_origin_path, fg='cyan')


@cli.command('-', help='delete dot(s).')
@click.option('-p', '--profile')
@click.argument('paths', nargs=-1, required=True)
def delete_dots(profile, paths):
	if not profile:
		profile = control.current_profile
	else:
		profile = Profile.get(control, profile)
	
	for path in paths:
		profile.delete_dot(path)


@cli.command('p', help='list profiles, or switch to a profile if specifed, which will be created if not existing yet.')
@click.argument('profile', nargs=1, required=False)
def list_or_switch_profile(profile):
	if profile:
		control.switch_profile(profile)
	else:
		for profile in control.iter_profiles():
			if profile.name == control.current_profile.name:
				click.secho('*', fg='green', nl=False)
			if profile.config['sync_type'] != 'local':
				click.secho('=', fg='cyan', nl=False)
			click.echo('\t', nl=False)
			click.echo(profile.name)


@cli.command('p=', help='set up remote profile.')
@click.argument('type') 
@click.argument('remote')
@click.argument('name', required=False)
def setup_remote_profile(type, remote, name=None, *args):
	Profile.create_from_remote(control, type, remote, name, *args)


@cli.command('p-', help='delete profile(s).')
@click.argument('profile', nargs=-1, required=True)
def delete_profiles(profile):
	for name in profile:
		if name == control.current_profile.name:
			click.secho('! keeping currently in use profile ', fg='red', nl=False)
			click.secho(name, fg='cyan')
			continue
		Profile.get(control, name).delete()


@cli.command('=+', help='set up sync.')
@click.argument('type')
@click.argument('remote', type=str)
def sync_setup(type, remote):
	control.current_profile.sync_setup(type, remote)


@cli.command('=.', context_settings=ctx_pass_through_args, help='commit changes. may add arguments of configured sync program.')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def commit_changes(args):
	try:
		control.current_profile.commit(*args)
	except Exception as e:
		click.secho('Error: ', fg='bright_red', nl=False)
		click.echo(e)


@cli.command('[=', context_settings=ctx_pass_through_args, help='pull from remote. may add arguments of configured sync program.')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def sync_pull(args):
	try:
		control.current_profile.sync_pull(*args)
	except Exception as e:
		click.secho('Error: ', fg='bright_red', nl=False)
		click.echo(e)


@cli.command('=]', context_settings=ctx_pass_through_args, help='push to remote. may add arguments of configured sync program.')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def sync_push(args):
	try:
		control.current_profile.sync_push(*args)
	except Exception as e:
		click.secho('Error: ', fg='bright_red', nl=False)
		click.echo(e)


@cli.command('=', context_settings=ctx_pass_through_args, help='list sync info, or run commands of configure sync program, if specifed.')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def sync_info_or_run_command(args):
	if len(args) is 0:
		click.secho('sync type', fg='cyan', nl=False)
		click.echo(': {}'.format(control.current_profile.config['sync_type']))
		click.secho('sync remote', fg='cyan', nl=False)
		click.echo(': {}'.format(control.current_profile.config['sync_remote']))
	else:
		try:
			control.current_profile.sync_command(*args)
		except Exception as e:
			click.secho('Error: ', fg='bright_red', nl=False)
			click.echo(e)


@cli.command('[-', help='discard last changes to dot(s).')
@click.argument('paths', nargs=-1, required=True)
def discard_changes(paths):
	for path in paths:
		control.current_profile.get_dot(path).link_back(overwrite=True)
