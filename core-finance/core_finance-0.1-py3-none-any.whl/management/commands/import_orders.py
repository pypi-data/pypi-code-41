import datetime
from decimal import Decimal
import xlrd

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    help = """
    Import a XLS file containing a list of Orders.

    Supports the format used by the Teaching Lab as of December 2018,
    with the following columns in the given order:

        - Description
        - Requester Name
        - Supplier
        - Amount (net)
        - Requisition Number
        - Req. date
        - Purchase Orders
        - Expense_Codes
        - Centro Responsabilidade
        - Project
        - Group
        - Payment Method
        - Notes
    """

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)
        parser.add_argument(
            "--no-header", action="store_false", help="disable header row"
        )

    def handle(self, *args, **options):

        errors = []

        workbook = xlrd.open_workbook(
            filename=options["filename"], encoding_override="utf-8", on_demand=True
        )
        worksheet = workbook.sheet_by_index(0)

        # start by validating the file structure
        #   - number, name and order of columns
        #   - empty cells

        expected_column_labels = [
            "Description",
            "Requester Name",
            "Supplier",
            "Amount (net)",
            "Requisition Number",
            "Req. date",
            "Purchase Orders",
            "Expense_Codes",
            "Centro Responsabilidade",
            "Project",
            "Group",
            "Payment Method",
            "Notes",
        ]
        expected_column_number = len(expected_column_labels)

        if worksheet.ncols != expected_column_number:
            raise CommandError(
                "Found %(found)s columns, expected exactly %(expected)s"
                % {"found": worksheet.ncols, "expected": expected_column_number}
            )

        for col, expected in zip(range(worksheet.ncols), expected_column_labels):
            if worksheet.cell_value(0, col) != expected:
                errors.append('Column "%s" not found' % expected)

        if errors:
            raise CommandError(errors)

        for col in range(worksheet.ncols):
            if col in [0, 2, 4, 5, 6, 7, 8, 9, 11, 12]:
                # ignore empty cells in columns for not mandatory fields:
                continue

            col_values = worksheet.col_values(col, start_rowx=2)
            empty_cells_row_indices = [
                i for i, value in enumerate(col_values) if value == ""
            ]
            for row in empty_cells_row_indices:
                cell = xlrd.formula.cellname(row, col)
                errors.append("Missing value in cell %s" % cell)

        if errors:
            raise CommandError(errors)

        # validate columns values
        # new entries must not have duplicated requisition numbers nor
        # purchase order number

        User = apps.get_model("auth", "User")
        AuthGroup = apps.get_model("auth", "Group")
        Currency = apps.get_model("finance", "Currency")
        OrderExpenseCode = apps.get_model("finance", "OrderExpenseCode")
        ExpenseCode = apps.get_model("finance", "ExpenseCode")
        FinanceProject = apps.get_model("finance", "FinanceProject")
        FinanceCostCenter = apps.get_model("finance", "FinanceCostCenter")
        Order = apps.get_model("finance", "Order")
        Supplier = apps.get_model("finance", "Supplier")

        self.stdout.write("Validating document...")

        imported_orders = []

        for row in range(1, worksheet.nrows):
            values = worksheet.row_values(row)

            # replace en-dash for single dash across all str values extracted
            values = [
                value.replace("\u2013", "-") if isinstance(value, str) else value
                for value in values
            ]

            values_raw = {
                col_name: value
                for col_name, value in zip(expected_column_labels, values)
            }

            # description --> TextField
            column_id = 0
            description = values_raw[expected_column_labels[column_id]]
            assert isinstance(description, str)

            # requester name --> CharField
            column_id = 1
            requester_name = values_raw[expected_column_labels[column_id]]
            assert "\n" not in requester_name, "Invalid requester name"
            assert isinstance(requester_name, str)

            # finance --> ForeignKey to Supplier
            column_id = 2
            supplier_name = values_raw[expected_column_labels[column_id]]
            assert "\n" not in supplier_name, "Invalid finance name"
            assert isinstance(supplier_name, str)
            if "_reimbursement" in supplier_name.lower():
                supplier_name = "Geral Reembolsos"
            if supplier_name.lower() == "":
                supplier = None
            else:
                try:
                    supplier = Supplier.objects.get(supplier_name=supplier_name.strip())
                except Supplier.DoesNotExist:
                    # Ignore missing suppliers in the DB
                    # Generate the report and warn the users to fill in
                    # the missing entries
                    supplier = None

                    msg = " ".join(
                        [
                            self.style.WARNING(f"Row {row+1:3d}:"),
                            f"Verify finance name '{supplier_name}'",
                        ]
                    )
                    self.stdout.write(msg)
                else:
                    assert isinstance(supplier, Supplier)

            # ammount --> DecimalField
            column_id = 3
            ammount = str(values_raw[expected_column_labels[column_id]])
            ammount = Decimal(ammount.strip())
            assert isinstance(ammount, Decimal)

            # requisition number --> IntegerField
            column_id = 4
            reqnum = int(values_raw[expected_column_labels[column_id]])
            try:
                order = Order.objects.get(order_reqnum=reqnum)
            except Order.DoesNotExist:
                # requisition number is valid, proceed
                pass
            else:
                if order.responsible.username in ["teresa.dias", "simone.zacarias"]:
                    msg = " ".join(
                        [
                            self.style.WARNING(f"Row {row+1:3d}:"),
                            f"Ignoring duplicated Order",
                        ]
                    )
                    self.stdout.write(msg)
                else:
                    msg = " ".join(
                        [
                            self.style.ERROR(f"Row {row+1:3d}:"),
                            f"Requisiton number {reqnum} already exists",
                        ]
                    )
                    self.stdout.write(msg)
                continue
            assert isinstance(reqnum, int)

            # requisition date --> DateField
            column_id = 5
            req_date = values_raw[expected_column_labels[column_id]]  # as float
            req_date = xlrd.xldate_as_tuple(req_date, workbook.datemode)
            req_date = datetime.datetime(*req_date).date()
            assert isinstance(req_date, datetime.date)

            # purchase order number --> CharField
            column_id = 6
            ponum = values_raw[expected_column_labels[column_id]]
            if ponum != "":
                try:
                    OrderExpenseCode.objects.get(purchase_order=ponum)
                except OrderExpenseCode.DoesNotExist:
                    assert ponum.startswith("EC")
                    if "," in ponum or ";" in ponum:
                        msg = " ".join(
                            [
                                self.style.WARNING(f"Row {row+1:3d}:"),
                                f"Using only the first Purchase Order number '{ponum}'",
                            ]
                        )
                        self.stdout.write(msg)
                        ponum = ponum.split(",")[0].split(";")[0]
                except OrderExpenseCode.MultipleObjectsReturned:
                    msg = " ".join(
                        [
                            self.style.WARNING(f"Row {row+1:3d}:"),
                            f"Multiple duplicated Purchase Order '{ponum}'",
                        ]
                    )
                    self.stdout.write(msg)
                else:
                    msg = " ".join(
                        [
                            self.style.WARNING(f"Row {row+1:3d}:"),
                            f"Duplicated Purchase Order '{ponum}'",
                        ]
                    )
                    self.stdout.write(msg)
            assert isinstance(ponum, str)

            # expense code --> ForeignKey to OrderExpenseCode
            column_id = 7
            expense_code_type = values_raw[expected_column_labels[column_id]]
            expense_code_type = expense_code_type.replace("&", "and")  # special case
            assert isinstance(expense_code_type, str)

            # cost center --> ForeignKey to FinanceCostCenter
            column_id = 8
            cost_center_code = int(values_raw[expected_column_labels[column_id]])
            cost_center_code = f"{cost_center_code:07d}"
            assert isinstance(cost_center_code, str)

            # finance project --> ForeignKey to FinanceProject
            column_id = 9
            finance_project_code = int(values_raw[expected_column_labels[column_id]])
            finance_project_code = f"{finance_project_code:03d}"
            assert isinstance(finance_project_code, str)

            # group --> ForeignKey to auth.Group
            column_id = 10
            auth_group_name = values_raw[expected_column_labels[column_id]]
            assert "\n" not in auth_group_name, "Invalid group name"
            assert isinstance(auth_group_name, str)
            if auth_group_name == "INDP":
                auth_group_name += " Lab"
            auth_group_name = f"GROUP: {auth_group_name}"
            try:
                group = AuthGroup.objects.get(name=auth_group_name.strip())
            except AuthGroup.DoesNotExist:
                raise CommandError("Invalid group name %s" % auth_group_name)
            assert isinstance(group, AuthGroup)

            # payment method --> CharField
            column_id = 11
            payment_method = values_raw[expected_column_labels[column_id]]
            for (
                payment_method_code,
                payment_method_name,
            ) in Order.PAYMENT_METHOD.items():
                if payment_method_name == payment_method.strip():
                    break
            else:
                raise CommandError("Payment Method mismatch: %s" % payment_method)
            payment_method = payment_method_code

            # notes --> TextField
            column_id = 12
            notes = values_raw[expected_column_labels[column_id]]
            assert isinstance(notes, str)

            # responsible --> (will be Simone by default)
            responsible = User.objects.get(username="simone.zacarias")

            # INTERLUDE: fetch the related tables required and build OrderExpenseCode
            try:
                cost_center = FinanceCostCenter.objects.get(
                    costcenter_code=cost_center_code
                )
            except FinanceCostCenter.DoesNotExist:
                raise CommandError("Invalid cost center code: %s" % cost_center_code)

            try:
                finance_project = FinanceProject.objects.get(
                    financeproject_code=finance_project_code, costcenter=cost_center
                )
            except FinanceProject.DoesNotExist:
                raise CommandError("Invalid project code: %s" % finance_project_code)

            try:
                expense_code = ExpenseCode.objects.get(
                    expensecode_type=expense_code_type, financeproject=finance_project
                )
            except ExpenseCode.DoesNotExist:
                raise CommandError("Invalid expense code: %s" % expense_code_type)

            # create Order
            order = Order(
                order_reqnum=reqnum,
                order_reqdate=req_date,
                order_desc=description,
                order_amount=ammount,
                order_req=requester_name,
                order_paymethod=payment_method,
                order_notes=notes,
                supplier=supplier,
                responsible=responsible,
                currency=Currency.objects.get(pk=1),  # EUR
                group=group,
            )
            order.save(
                expensecode_kwargs={
                    "expensecode": expense_code,
                    "purchase_order": ponum,
                }
            )

            imported_orders.append(order)

        self.stdout.write(
            self.style.SUCCESS("Imported %d orders" % len(imported_orders))
        )
