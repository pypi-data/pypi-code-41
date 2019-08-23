from .publication.publication import Publication, PubType
from .project import Project
from .journal import Journal, JournalImpactFactor, JournalAlias
from .author_alias import AuthorAlias


# ############################################################################
# class FinanceCostCenter(models.Model):

#     center_id = models.AutoField(primary_key=True)          #: ID
#     center_name = models.CharField('Name', max_length=200)  #: Name
#     center_code = models.CharField('Code', max_length=200)  #: Code

#     class Meta:
#         ordering = ['center_name',]
#         verbose_name = "Cost Center"
#         verbose_name_plural = "Cost Centers"

#     def __str__(self):
#         return self.center_name
# #############################################################################
# class FinanceProject(models.Model):

#     financeproject_id = models.AutoField(primary_key=True)                          #: ID
#     financeproject_name = models.CharField('Name', max_length=200)                  #: Name
#     financeproject_number = models.IntegerField('Number', blank=True, null=True)    #: Number
#     costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.CASCADE)   #: Finance Cost Center is a Fk to that table
#     group = models.ForeignKey(Group, on_delete=models.CASCADE)                    #: Research group use this project. is a Fk to the Group table


#     class Meta:
#         ordering = ['financeproject_name',]
#         verbose_name = "Finance Project"
#         verbose_name_plural = "Finance Projects"

#     def __str__(self):
#         return self.financeproject_name


# ##################################################################################
