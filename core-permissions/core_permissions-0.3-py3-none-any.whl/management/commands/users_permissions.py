from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from humanresources.models import Contract, ContractProposal
from people.models import Person

class Command(BaseCommand):
    help = 'List all users permissions'


    def handle(self,  *args, **options):
        
        for user in User.objects.all().order_by('username'):

            contracts = Contract.objects.list_permissions(user).order_by('person__full_name')
            proposals = ContractProposal.objects.list_permissions(user).order_by('person__full_name')
            people    = Person.objects.list_permissions(user).order_by('full_name')

            report = False

            try:
                person = Person.objects.get(auth_user=user)
            except Person.DoesNotExist:
                person = None

            for o in contracts:
                if o.person!=person:
                    report = True
                    break

            for o in proposals:
                if o.person!=person or o.person is None:
                    report = True
                    break

            for o in people:
                if o!=person:
                    report = True
                    break

            if report:
                print(
                    '\033[92m',   str(user), '\033[0m',
                    'Contracts:', '\033[91m', len(contracts), '\033[0m'
                    'Proposals:', '\033[91m', len(proposals), '\033[0m'
                    'People:',    '\033[91m', len(people),    '\033[0m')
                
                if len(contracts)<=300:
                    print('\tCONTRACTS: ','\n\t\t'+'\n\t\t'.join([str(c) for c in contracts]))
                else:
                    print('\tCONTRACTS:','\033[91m', len(contracts),'\033[0m')

                if len(proposals)<=300:
                    print('\tPROPOSALS: ','\n\t\t'+'\n\t\t'.join([str(c) for c in proposals]))
                else:
                    print('\tPROPOSALS:','\033[91m', len(proposals),'\033[0m')


                if len(people)<=300:
                    print('\tPEOPLE: ','\n\t\t'+'\n\t\t'.join([str(c) for c in people]))
                else:
                    print('\tPEOPLE:','\033[91m', len(people),'\033[0m')

        print()
        #################################################################################