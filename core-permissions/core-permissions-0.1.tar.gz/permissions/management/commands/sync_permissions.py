from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from permissions.models import Permission as RankedPermissions
from people.models import Group as ResearchGroup
from people.models import GroupType as ResearchGroupType

from humanresources.models import Contract
from humanresources.models import ContractProposal
from people.models import Person
from orders.models import Order


PROFILE_GROUP_NAME_TEMPLATE = 'PROFILE: Group {}: {}'

PROFILE_RANKS = {
    'coordinator': 300,
    'admin': 200,
    'manager': 100,
}


def get_permission(model, codename):
    content_type = ContentType.objects.get_for_model(model)
    if codename in ('add', 'view', 'change', 'delete'):
        codename = f'{codename}_{content_type.model}'
    return Permission.objects.get(
        content_type=content_type,
        codename=codename,
    )


DEFAULT_PERMISSIONS = {
    'coordinator': {
        get_permission(Person, 'view'),
        get_permission(Person, 'change'),
        get_permission(Person, 'app_access_people'),

        get_permission(ContractProposal, 'add'),
        get_permission(ContractProposal, 'view'),
        get_permission(ContractProposal, 'change'),

        get_permission(Contract, 'view'),

        get_permission(Order, 'add'),
        get_permission(Order, 'view'),
        get_permission(Order, 'change'),
        get_permission(Order, 'delete'),
        get_permission(Order, 'app_access_orders'),
    },
    'admin': {
        get_permission(Person, 'view'),
        get_permission(Person, 'change'),
        get_permission(Person, 'app_access_people'),

        get_permission(ContractProposal, 'add'),
        get_permission(ContractProposal, 'view'),
        get_permission(ContractProposal, 'change'),

        get_permission(Contract, 'view'),

        get_permission(Order, 'add'),
        get_permission(Order, 'view'),
        get_permission(Order, 'change'),
        get_permission(Order, 'delete'),
        get_permission(Order, 'app_access_orders'),
    },
    'manager': {
        get_permission(Person, 'view'),
        get_permission(Person, 'change'),
        get_permission(Person, 'app_access_people'),

        get_permission(ContractProposal, 'add'),
        get_permission(ContractProposal, 'view'),
        get_permission(ContractProposal, 'change'),

        get_permission(Contract, 'view'),

        get_permission(Order, 'add'),
        get_permission(Order, 'view'),
        get_permission(Order, 'change'),
        get_permission(Order, 'delete'),
        get_permission(Order, 'app_access_orders'),
    },
}


class Command(BaseCommand):
    help = 'Sync Authorization Profiles with existing Research Groups'

    def add_arguments(self, parser):
            parser.add_argument('group_id', nargs='*', type=int)

            parser.add_argument(
                '--list',
                action='store_true',
                dest='list',
                help='List research groups and their IDs',
            )

            parser.add_argument(
                '--default',
                action='store_true',
                dest='default',
                help='Set the default permissions',
            )

    def handle(self,  *args, **options):

        if options['list']:
            self._list_groups()
        elif options['group_id']:
            # sync the selected groups
            for group_id in options['group_id']:
                research_group = ResearchGroup.objects.get(group_id=group_id)
                self._sync_group(research_group, **options)
        else:
            # sync all groups
            for research_group in ResearchGroup.objects.all():
                self._sync_group(research_group, **options)

    def _is_platform(self, research_group):
        platform_type = ResearchGroupType.objects.get(grouptype_name='Platforms')
        return research_group.grouptype == platform_type

    def _list_groups(self):
        header = '[ID]\tNAME'
        self.stdout.write(header + '\n' + '=' * 79)
        for group in ResearchGroup.objects.all().order_by('pk'):
            self.stdout.write(f'[{group.group_id:2}]\t{group.group_name}')

    def _sync_group(self, research_group, **options):
        self.stdout.write("Synchronizing Research Group "
                          f"[{research_group.group_id:2}] {research_group}")

        for profile in PROFILE_RANKS.keys():

            if profile == 'coordinator' and not self._is_platform(research_group):
                # coordinator are only configures for Platforms
                continue

            self.stdout.write(f"  Profile: {profile.title():14}", ending="")

            name = PROFILE_GROUP_NAME_TEMPLATE.format(
                profile.title(), research_group.group_name)

            if 'Advanced BioImaging and BioOptics Experimental Platform' in name:
                # name too long for AuthGroup.name
                name = name.replace(
                    'Advanced BioImaging and BioOptics Experimental Platform',
                    'ABBE'
                )

            auth_group, created = AuthGroup.objects.get_or_create(name=name)

            # make sure the Group Head is assigned to the Admin Profile
            if profile == 'admin':
                try:
                    group_admin_user = research_group.person.auth_user
                except AttributeError:
                    # no person is assigned as Group Head
                    pass
                else:
                    group_admin_user.groups.add(auth_group)

            if created:
                RankedPermissions.objects.create(
                    djangogroup=auth_group,
                    researchgroup=research_group,
                    ranking=PROFILE_RANKS[profile],
                )

            if created or options['default']:
                auth_group.permissions.add(*DEFAULT_PERMISSIONS[profile])

            # check if current permissions are the default ones
            permissions_set = set(auth_group.permissions.all())
            symdiff = DEFAULT_PERMISSIONS[profile] ^ permissions_set

            if symdiff:
                status = self.style.ERROR(u'\uFF01')
            else:
                status = self.style.SUCCESS(u'\u2714')

            self.stdout.write(status)
