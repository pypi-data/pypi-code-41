from django.db import models


class OrderFile(models.Model):

    file      = models.FileField(upload_to='orders/orders_files', max_length=255)
    createdon = models.DateField('Created on', auto_now_add=True)
    createdby = models.ForeignKey('auth.User', verbose_name='Created by', on_delete=models.CASCADE)

    order     = models.ForeignKey('Order', blank=True, null=True, on_delete=models.CASCADE)

    class Meta:        
        ordering = ['createdon',]
        verbose_name = "Order file"
        verbose_name_plural = "Orders files"