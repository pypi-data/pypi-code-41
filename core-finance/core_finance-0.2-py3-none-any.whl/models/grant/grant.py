from django.db import models

class Grant(models.Model):
    """
    Represents a Grant in the system
    Example: PZLOC
    """
    name = models.CharField('Name', max_length=200)  #: Name

    nationality = models.ForeignKey('common.Nationality', verbose_name='Grant nationality', on_delete=models.CASCADE)
    domain      = models.ForeignKey('GrantDomain', verbose_name='Grant domain', on_delete=models.CASCADE)
    grantor     = models.ForeignKey('FinancingAgency', verbose_name='Grantor', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Grant"
        verbose_name_plural = "Grants"

    def __str__(self):
        return self.name
