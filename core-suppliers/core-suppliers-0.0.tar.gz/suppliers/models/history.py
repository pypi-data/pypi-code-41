from django.contrib.auth.models import User
from django.db import models


class Tophistory(models.Model):
    """
    Represents a historic time of payment of a finance in the system
    """

    tophistory_id   = models.AutoField(primary_key=True)  #: Pk ID
    tophistory_top  = models.CharField('TOP', max_length=100) #: Time of paymeny
    tophistory_date = models.DateField('Date', blank=True, null=True) #: Historic time of table date

    createdby = models.ForeignKey(User, related_name='createdby', verbose_name='Created by', on_delete=models.CASCADE) #: the user that created this top
    supplier  = models.ForeignKey('Supplier', blank=True, null=True, on_delete=models.CASCADE) #: Fk Supplier for this historic top

    class Meta:
        verbose_name = "TOP History"
        verbose_name_plural = "Top Histories"

    def supplier_id(self):
        return str( self.supplier.supplier_id )

    def __str__(self):
        return self.tophistory_top
