from django.db import models
from django.utils.html import format_html

class GroupBudget(models.Model):
    """
    Represents a Budget for a certain Group in the system
    This table is a view in MySql and should'nt be considered as a table in the data base
    This table is used only for reports presentation
    """

    costcenter_code     = models.CharField('Costcenter Code', max_length=200)  #: Code
    financeproject_code = models.CharField('Financeproject Code', max_length=200)    #: Number
    expensecode_number  = models.CharField('Expensecode Number', max_length=100) #: Name
    costcenter_name     = models.CharField('Costcenter Name', max_length=200)  #: Name
    financeproject_name = models.CharField('Financeproject Name', max_length=200) #: Name
    expensecode_type    = models.CharField('Expensecode Type', max_length=100) #: Type
    budget_amount       = models.DecimalField('Budgeted amount', max_digits=11, decimal_places=2)    #: Amount for that budget
    group               = models.ForeignKey('auth.Group', verbose_name='Group', blank=False, null=False, on_delete=models.PROTECT) #: Research group use this project. is a Fk to the Group table
    budget_year         = models.IntegerField('Year', blank=True, null=True)  #: Budget year
    orders_amount       = models.IntegerField('Orders amount', blank=True, null=True)  #: Orders amount

    def project_orders(self):
        from ..project.project import Project
        project = Project.objects.get(financeproject_code=self.financeproject_code, costcenter__costcenter_code=self.costcenter_code)
        return format_html("<a href='/export/orders_from_project/%d/' >Project orders</a>" % project.pk)
    project_orders.short_description = 'Finance project orders'
    project_orders.allow_tags = True

    def delete(self): pass

    class Meta:
        #ordering = ['budget_year']
        verbose_name = "Group Budget Report"
        verbose_name_plural = "Group Budget Reports"
        #unique_together = (('budget_year','expensecode'),)
        managed = False
        app_label = 'finance'

    def __str__(self):
        return str(self.group)
