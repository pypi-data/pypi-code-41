from django.db import models
from .project_queryset import ProjectQuerySet

class Project(models.Model):
    """
    Represents Project in the system
    """
    name = models.CharField('Name', max_length=200) #: Name
    code = models.CharField('Code', max_length=200, unique=True) #: Number

    # Grant section
    start_date   = models.DateField('Starting date', blank=True, null=True,
                                    help_text='Starting date of the grant')
    end_date     = models.DateField('Ending date', blank=True, null=True,
                                    help_text='Ending date of the grant')
    total_amount = models.DecimalField('Total amount', blank=True, null=True, max_digits=11, decimal_places=2,
                                       help_text='Total amount of the grant')
    overheads    = models.DecimalField('Overhead', blank=True, null=True, max_digits=11, decimal_places=2,
                                      help_text='Overhead amount of the grant')
    funding      = models.DecimalField('Funding', blank=True, null=True, max_digits=11, decimal_places=2,
                                      help_text='Funding amount of the grant')

    responsible = models.ForeignKey('people.Person', on_delete=models.CASCADE)
    costcenter  = models.ForeignKey('CostCenter', verbose_name='Cost Center', on_delete=models.CASCADE)
    currency    = models.ForeignKey('common.Currency', verbose_name='Currency', blank=True, null=True, on_delete=models.CASCADE)
    grant       = models.ForeignKey('Grant', verbose_name='Grant', blank=True, null=True, on_delete=models.CASCADE)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ['code', 'costcenter']
        verbose_name = "Finance Project"
        verbose_name_plural = "Finance Projects"

    def __str__(self):
        costcenter = self.costcenter
        if costcenter!=None:
            return costcenter.code + "-" + self.code + ": " + costcenter.name + "-" + self.name
        else:
            return "No FinanceCostCenter associated - " + self.name + " - " + self.code

    # Custom methods

    def nationality(self):
        if self.grant is None:
            return ""
        return str(self.grant.nationality)

    def domain(self):
        if self.grant is None:
            return ""
        return str(self.grant.domain)

    def grantor(self):
        if self.grant is None:
            return ""
        return str(self.grant.grantor)



    @staticmethod
    def autocomplete_search_fields():
        return (
            'name__icontains',
            'code__icontains',
            'costcenter__name__icontains',
            'costcenter__code__icontains'
        )
