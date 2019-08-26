from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Q
from django.template.defaultfilters import pluralize

from humanresources.utils import send_mail


class Command(BaseCommand):
    help = "Inspect all Orders in the DB for inconsistencies."

    def add_arguments(self, parser):
        parser.add_argument("--responsible", type=str, nargs="+")
        parser.add_argument("--notify", action="store_true")

    def handle(self, *args, **options):
        User = apps.get_model("auth", "User")
        Order = apps.get_model("finance", "Order")

        users_to_notify = []
        optional_filters = Q()

        if options["responsible"]:
            for username in options["responsible"]:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    raise CommandError("User '%s' not found" % username)
                users_to_notify.append(user)
                optional_filters.add(Q(responsible=user), Q.OR)

        # apply initial filters
        orders = Order.objects.filter(optional_filters)

        self.stdout.write(f"Found {orders.count()} Orders")

        if options["responsible"]:
            self.stdout.write(
                f"Found {orders.count()} Orders belonging to user{pluralize(options['responsible'])} {', '.join([repr(u) for u in options['responsible']])}"
            )

        orders_missing_supplier = orders.filter(supplier__isnull=True)
        if orders_missing_supplier:
            self.stdout.write(
                self.style.WARNING(
                    f"{orders_missing_supplier.count()} Orders are missing a Supplier"
                )
            )

        all_warnings = orders_missing_supplier

        if all_warnings and options["responsible"] and options["notify"]:
            # Send a notification email to each user with inconsistent data records

            subject = "Data quality report"

            for user in users_to_notify:
                if not all_warnings.filter(responsible=user):
                    continue

                orders_missing_supplier = all_warnings.filter(
                    responsible=user
                ).order_by('order_reqdate')

                recipient_list = [user.email]

                message_context = {
                    "base_url": settings.BASE_URL,
                    "orders_missing_supplier": orders_missing_supplier,
                }

                send_mail(subject, recipient_list, message_context)

                self.stdout.write(self.style.SUCCESS(f"Report sent to {user.email}"))
        elif all_warnings and options["responsible"] and not options["notify"]:
            self.stdout.write(
                "Pass the optional argument '--notify' to send an email to the users above"
            )
        elif all_warnings and not options["responsible"] and options["notify"]:
            users_to_warn = [
                User.objects.get(id=user_id)
                for user_id in all_warnings.values_list("responsible", flat=True)
                .distinct()
                .order_by("responsible__username")
            ]
            for user in users_to_warn:
                user_orders = all_warnings.filter(responsible=user)
                print(f"  {user_orders.count():3d} belonging to user '{user}'")
            self.stdout.write(
                self.style.ERROR(
                    "Mass notification is disabled, please select the users you wish to notify"
                )
            )
            self.stdout.write(
                "Pass the argument '--reponsible <user1> <user2>' to send an email to the selected users"
            )
        else:
            self.stdout.write("Nothing to report.")
