from git_profiles.commands.add_profile import AddProfile
from git_profiles.commands.current_profile import CurrentProfile
from git_profiles.commands.del_profile import DelProfile
from git_profiles.commands.destroy_profiles import DestroyProfiles
from git_profiles.commands.list_profiles import ListProfiles
from git_profiles.commands.show_profile import ShowProfile
from git_profiles.commands.update_profile import UpdateProfile
from git_profiles.commands.use_profile import UseProfile


def execute_command(args: any) -> None:
    commands = {
        "add": AddProfile,
        "use": UseProfile,
        "del": DelProfile,
        "show": ShowProfile,
        "list": ListProfiles,
        "update": UpdateProfile,
        "current": CurrentProfile,
        "destroy": DestroyProfiles,
    }

    command = commands.get(args.command, None)
    if command:
        instance = command(args)
        instance.execute()
