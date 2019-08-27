from django.db import models


class ScientificArea(models.Model):
    """
    Represents the Scientific Area of a person
    Example: Neuroscience, Medicine
    """
    name = models.CharField('Name', max_length=100)  #: Name

    class Meta:
        ordering = ['name',]
        verbose_name = "Scientific area"
        verbose_name_plural = "Scientific areas"


    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains", )
