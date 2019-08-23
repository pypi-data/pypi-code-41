from django.db import models
from .history import Tophistory


class Supplier(models.Model):
    """
    Represents a Supplier in the systemcurrency
    """
    name      = models.CharField('Name', max_length=200)
    nif       = models.CharField('NIF Number', max_length=50, blank=True, null=True)
    keywords  = models.CharField('Keywords', max_length=200, blank=True, null=True)
    contact   = models.CharField('Contact person', max_length=200, blank=True, null=True)
    phone     = models.CharField('Phone Number', max_length=200, blank=True, null=True)
    email     = models.CharField('Email', max_length=200, blank=True, null=True)
    discounts = models.CharField('Discounts', max_length=200, blank=True, null=True)

    country  = models.ForeignKey('common.Country', blank=True, null=True, on_delete=models.CASCADE)
    category = models.ManyToManyField('Category', blank=True)

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains", "keywords__icontains")

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ['name',]

    def __str__(self):
        return self.name

    def top(self):
        """
        The function will order the top Histories payment in the finance page according to their creation order
        so the last top in this page his the last created top
        In the admin list of suppliers we will see the last created top
        """
        return Tophistory.objects.filter(supplier=self).order_by('-pk').first()

    def categories_str(self):
        """
        The function will present all the categories for this finance in one line
        in the admin list of suppliers
        """
        return ", ".join([str(cat) for cat in self.category.all()])
