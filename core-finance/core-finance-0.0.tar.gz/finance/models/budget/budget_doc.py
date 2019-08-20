import urllib

import xlrd
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe




def build_missing_related_object_message(model, obj_repr, msg='', *args, **kwargs):
    """Returns a safe HTML message indicating that the parsed `obj_repr`
    does not exist in the database and provides a link to its add form.

    Extra `args` are used to format a custom message. Passing `kwargs`
    will populate the add form with initial data.

    Example::

        build_missing_related_object_message(
            FinanceCostCenter,
            '123456 - Super Cost Center',
            costcenter_code=cost_center_code,
            costcenter_name=cost_center_name,
        )

    Example with a custom message (notice that `model` and `obj_repr`
    are available for formatting)::

        build_missing_related_object_message(
            Budget,
            None,
            '{model._meta.verbose_name} for year {} with Expense Code {} does not exist',
            self.year,
            expense_code.abbrv,
            budget_year=self.year,
            budget_amount=amount,
            expensecode=expense_code.pk,
        )
    """

    if msg:
        msg = msg.format(*args, model=model, obj_repr=obj_repr)
    else:
        msg = f'{model._meta.verbose_name} "{obj_repr}" does not exist.'
    # TODO build url for pyforms app
    url = reverse(f'admin:{model._meta.app_label}_{model._meta.model_name}_add')
    url = url + '?' + urllib.parse.urlencode(kwargs)
    link = f'<a href="{url}" target="_blank">Click to add</a>'
    return mark_safe(msg + ' ' + link)





class BudgetDoc(models.Model):

    document = models.FileField(upload_to='documents/%Y/%m/%d')
    year     = models.IntegerField('Year')

    class Meta:
        verbose_name = 'Budget document'

    def __str__(self):
        return self.document.name

    def save(self):
        super().save()

        title = f'The following budgets for the year {self.year} were updated:'
        entry_template = '<li>{}: new amount is {:.2f} \u20AC</li>'

        update_report = title

        for budget, amount in self.budgets_to_update:
            budget.budget_amount = amount
            budget.save()

            update_report += entry_template.format(
                budget.expensecode.abbrv, amount)

        self.update_report = mark_safe(update_report)



    def clean(self):
        """
        Custom clean method to verify the uploaded file is valid and that
        the objects required are already present in the database.
        """

        if not self.document:
            # skip file content validation if no file was selected
            return

        from finance.models import Budget
        from finance.models import CostCenter
        from finance.models import Project
        from finance.models import ExpenseCode

        budgets_to_update = []
        errors = []

        workbook = xlrd.open_workbook(
            file_contents=self.document.read(),
            encoding_override='utf-8',
            on_demand=True,
        )
        worksheet = workbook.sheet_by_index(0)

        # start by validating the file structure
        #   - number, name and order of columns
        #   - empty cells

        expected_column_labels = [
            'Projecto',
            'Centro Responsabilidade',
            'Grupo Despesa',
            'Data',
            'Valor',
        ]
        expected_column_number = len(expected_column_labels)

        if worksheet.ncols != expected_column_number:
            raise ValidationError(
                'Found %(found)s columns, expected exactly %(expected)s',
                params={
                    'found': worksheet.ncols,
                    'expected': expected_column_number,
                }
            )

        for col, expected in zip(range(worksheet.ncols), expected_column_labels):
            if worksheet.cell_value(0, col) != expected:
                errors.append('Column "%s" not found' % expected)

        if errors:
            raise ValidationError(errors)

        for col in range(worksheet.ncols):
            col_values = worksheet.col_values(col, start_rowx=2)
            empty_cells_row_indices = [
                i for i, value in enumerate(col_values) if value == ''
            ]
            for row in empty_cells_row_indices:
                cell = xlrd.formula.cellname(row, col)
                errors.append('Missing value in cell %s' % cell)

        if errors:
            raise ValidationError(errors)

        # validate columns values
        # due to model relationships the validation order must be:
        #   1. cost center
        #   2. finance project (requires cost center)
        #   3. expense code (required project)
        #   4. budget (requires expense code)


        for row in range(2, worksheet.nrows):
            values = worksheet.row_values(row)

            # replace en-dash for single dash across all str values extracted
            values = [
                value.replace(u"\u2013", '-')
                if isinstance(value, str) else value
                for value in values
            ]

            project_raw, cost_center_raw, expense_code_raw, _, amount = values

            expense_code = None

            # 1. cost center

            cost_center_code, cost_center_name = cost_center_raw.split(' - ', 1)
            cost_center_code = cost_center_code.zfill(7)
            try:
                cost_center = CostCenter.objects.get(
                    costcenter_code=cost_center_code,
                )
            except CostCenter.DoesNotExist:
                errors.append(
                    build_missing_related_object_message(
                        CostCenter,
                        cost_center_raw,
                        costcenter_code=cost_center_code,
                        costcenter_name=cost_center_name,
                    )
                )
                continue

            # 2. finance project

            project_code, project_name = project_raw.split(' - ', 1)
            project_code = project_code.zfill(3)
            try:
                project = Project.objects.get(
                    financeproject_code=project_code,
                    costcenter=cost_center,
                )
            except Project.DoesNotExist:
                errors.append(
                    build_missing_related_object_message(
                        Project,
                        project_raw,
                        financeproject_code=project_code,
                        financeproject_name=project_name,
                        costcenter=cost_center.pk,
                    )
                )
                continue

            # 3. expense code

            expense_code_number, expense_code_name = expense_code_raw.split(' - ', 1)
            expense_code_number = expense_code_number.zfill(2)
            try:
                expense_code = ExpenseCode.objects.get(
                    expensecode_number=expense_code_number,
                    expensecode_type=expense_code_name,
                    financeproject=project,
                )
            except ExpenseCode.DoesNotExist:
                errors.append(
                    build_missing_related_object_message(
                        ExpenseCode,
                        expense_code_raw,
                        expensecode_number=expense_code_number,
                        expensecode_type=expense_code_name,
                        financeproject=project.pk,
                    )
                )
                continue

            # 4. budget

            try:
                budget = Budget.objects.get(
                    expensecode=expense_code,
                    budget_year=self.year,
                )
            except Budget.DoesNotExist:
                errors.append(
                    build_missing_related_object_message(
                        Budget,
                        None,
                        '{model._meta.verbose_name} for year {} with Expense Code {} does not exist',
                        self.year,
                        expense_code.abbrv,
                        budget_year=self.year,
                        budget_amount=amount,
                        expensecode=expense_code.pk,
                    )
                )
                continue

            budgets_to_update.append(
                (budget, amount)
            )

        if errors:
            raise ValidationError(list(set(errors)))

        self.budgets_to_update = budgets_to_update

