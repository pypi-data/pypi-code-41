from django.db import models
from suppliers.models import history


class Supplier(models.Model):
    """
    Represents a Supplier in the systemcurrency
    """
    supplier_id = models.AutoField(primary_key=True)  #: Pk ID
    supplier_name = models.CharField('Name', max_length=200) #: Name
    supplier_nif = models.CharField('NIF Number',max_length=50, blank=True, null=True) #: NIF number
    supplier_keywords = models.CharField('Keywords', max_length=200, blank=True, null=True) #: Free text Keywords
    supplier_contact = models.CharField('Contact Person', max_length=200, blank=True, null=True) #: The mani contact person of a finance
    supplier_phone = models.CharField('Phone Number', max_length=200, blank=True, null=True) #: Phone number of a finance
    supplier_mail = models.CharField('Email', max_length=200, blank=True, null=True) #: Email address of a finance
    supplier_discounts = models.CharField('Discounts', max_length=200, blank=True, null=True) #: Free text Discounts

    country = models.ForeignKey('common.Country', blank=True, null=True, on_delete=models.CASCADE) #: Fk Supplier's operation country
    category = models.ManyToManyField('Category', blank=True)  #: category of the supplied product

    @staticmethod
    def autocomplete_search_fields():
        return ("supplier_name__icontains","supplier_keywords__icontains")

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ['supplier_name',]

    def __str__(self):
        return self.supplier_name

    def top_(self):
        """
        The function will order the top Histories payment in the finance page according to their creation order
        so the last top in this page his the last created top
        In the admin list of suppliers we will see the last created top
        """
        tops = history.Tophistory.objects.filter(supplier=self).order_by('-tophistory_id')
        if len(tops)>0:
            return tops[0].tophistory_top
        else:None
        return None

    def categories_(self):
        """
        The function will present all the categories for this finance in one line
        in the admin list of suppliers
        """
        listOfRes = []
        for cat in self.category.all(): listOfRes.append(str(cat))
        return ", ".join(listOfRes)
