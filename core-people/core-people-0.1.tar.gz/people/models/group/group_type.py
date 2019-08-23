from django.db import models

class GroupType(models.Model):
    """
    Represents a Type of a Group in the system
    Example: Fellow, Staff
    """
    name = models.CharField('Name', max_length=200)   #: Name

    class Meta:
        ordering = ['name',]
        verbose_name = "Group type"
        verbose_name_plural = "Group types"

    def __str__(self):
        return self.name



