from django.db import models

class ExpenseCode(models.Model):
    """
    Represents a Budget of an order in the system
    """

    number = models.CharField('ExpenseCode Number', max_length=100) #: Name
    type = models.CharField('ExpenseCode Type', max_length=100) #: Type

    project = models.ForeignKey('finance.Project', verbose_name='Finance project', on_delete=models.CASCADE)

    @staticmethod
    def autocomplete_search_fields():
        return (
            "number__icontains",
            'type__icontains',
            'project__name__icontains',
            'project__code__icontains',
            'project__costcenter__name__icontains'
        )


    class Meta:
        verbose_name = "Expense code"
        verbose_name_plural = "Expense codes"
        unique_together = ("number", "project")

    def __str__(self):
        return self.project.costcenter.code + "-" + \
               self.project.code + "-" + \
               self.number + ": " + self.project.costcenter.name + "-" + \
               self.project.name + "-" + self.type

    def expensecode(self):
        return str(self.project.costcenter.code + "-" + \
                   self.project.code + "-" + \
                   self.number + ": " + self.project.costcenter.name + "-" + \
                   self.project.name + "-" + self.type)

    @property
    def abbrv(self):
        """Returns a string with codes only, i.e. `CCCCCCC-PPP-EE`."""
        cost_center = self.project.costcenter.code
        project = self.project.code
        expense_code = self.number
        return f'{cost_center}-{project}-{expense_code}'
