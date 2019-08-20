from django.db import models


class Category(models.Model):
    """
    Represents Product Category in the system
    """
    name = models.CharField('Name', max_length=100, unique=True) #: Name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    
    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)
