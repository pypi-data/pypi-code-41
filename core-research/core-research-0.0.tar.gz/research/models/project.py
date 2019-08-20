from django.db import models



class Project(models.Model):
    """
    Represents a Research Project of a Group in the system
    Example: Lima, Costa
    """

    project_id = models.AutoField(primary_key=True)             #: ID
    project_name = models.CharField('Project', max_length=200)  #: Name
    project_desc = models.TextField('Description', default='')  #: Description of the Project
    project_collaborators = models.CharField('Collaborators', max_length=200, blank=True, null=True)    #: Name of the collaborators of the Project
    project_funding = models.CharField('Funding', max_length=200, blank=True, null=True)                #: Funding of the project e.g. ERC
    project_order = models.IntegerField('Order', blank=True, null=True)                                 #: Number of orders e.g. 3
    project_active = models.NullBooleanField('Active')                                                      #: Check Box Is the Project is Active?

    group = models.ForeignKey('people.Group', verbose_name='Group',
                              on_delete=models.CASCADE)  #: Fk to the Group table. e.g. Lima

    class Meta:
        ordering = ['project_name',]
        verbose_name = "Project"
        verbose_name_plural = "Groups - Projects"
        app_label = 'research'

    def __str__(self):
            return self.project_name
