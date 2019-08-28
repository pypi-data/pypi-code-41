# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal

from django.db import models
from django.db.models import Sum

from djangoldp.models import Model
from djangoldp_project.models import Customer
from djangoldp_project.models import Project


class FreelanceInvoice(Model):
    # customer = models.ForeignKey(User, on_delete=models.CASCADE)
    # provider = models.ForeignKey(User, on_delete=models.CASCADE)
    STATES = (
        ('pending', 'en attente'),
        ('sent', 'envoyé'),
        ('paid', 'payé')
    )
    TVA_RATES = (
        (0.0, 'exonération de TVA'),
        (20.0, '20%')
    )
    freelanceFullname = models.CharField(max_length=255)
    identifier = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Titre facture")
    state = models.CharField(max_length=255, choices=STATES, default='pending')
    htAmount = models.DecimalField(max_digits=11, decimal_places=2)
    tvaRate = models.DecimalField(choices=TVA_RATES, max_digits=4, decimal_places=2, default=20.0)
    uploadUrl = models.URLField(blank=True, null=True)
    creationDate = models.DateField(auto_now_add=True)
    modificationDate = models.DateField(auto_now=True)
    invoicingDate = models.DateField(default=datetime.date.today)

    class Meta:
        container_path = "freelance-invoices/"
        permissions = (
            ('view_freelance_invoice', 'Read'),
            ('control_freelance_invoice', 'Control'),
        )
        rdf_type = 'hd:freelanceinvoice'
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add']
        owner_perms = ['inherit', 'change', 'control', 'delete']

    def __str__(self):
        return '{} ({} / {})'.format(self.freelanceFullname, self.identifier, self.title)


class CustomerInvoice(Model):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, null=True)
    STATES = (
        ('pending', 'en attente'),
        ('paid', 'réglée')
    )
    identifier = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    state = models.CharField(max_length=255, choices=STATES, default='pending')
    tvaRate = models.DecimalField(max_digits=4, decimal_places=2)
    creationDate = models.DateField(auto_now_add=True)
    modificationDate = models.DateField(auto_now=True)
    invoicingDate = models.DateField(default=datetime.date.today)
    additionalText = models.CharField(max_length=255, blank=True, null=True)

    def htAmount(self):
        amount = Task.objects.filter(batch__invoice = self).aggregate(total=Sum('htAmount'))['total']
        if amount is None:
            amount = Decimal(0.0)
        return amount


    def tvaAmount(self):
        return Decimal(self.tvaRate * self.htAmount() / Decimal(100))

    def ttcAmount(self):
        return Decimal(self.tvaAmount() + self.htAmount())

    class Meta:
        depth = 2
        container_path = "customer-invoices/"
        nested_fields = ["batches", "project", "customer"]
        serializer_fields = ["@id", "identifier", "title", "state", "htAmount", "tvaRate", "invoicingDate",
                             "tvaAmount", "ttcAmount", "batches", "project", "customer"]
        permissions = (
            ('view_invoice', 'Read'),
            ('control_invoice', 'Control'),
        )
        rdf_type = 'hd:customerinvoice'
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add']
        owner_perms = ['inherit', 'change', 'control', 'delete']

    def __str__(self):
        return '{} - {} ({})'.format(self.identifier, self.title, self.htAmount())


# Lot =========================================================
class Batch(Model):
    invoice = models.ForeignKey(CustomerInvoice, on_delete=models.CASCADE, related_name='batches')
    title = models.CharField(max_length=255)
    creationDate = models.DateField(auto_now_add=True)
    modificationDate = models.DateField(auto_now=True)

    class Meta:
        nested_fields = ["tasks"]
        serializer_fields = ['@id', 'invoice', 'title', 'htAmount', 'tasks']
        permissions = (
            ('view_batch', 'Read'),
            ('control_batch', 'Control'),
        )
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add']
        owner_perms = ['inherit', 'change', 'control', 'delete']

    def __str__(self):
        return '{} - {} ({} € HT)'.format(self.invoice.title, self.title, self.htAmount())

    def htAmount(self):
        amount = self.tasks.all().aggregate(total=Sum('htAmount'))['total']
        if amount is None:
            amount = Decimal(0.0)
        return amount


class Task(Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    htAmount = models.DecimalField(max_digits=11, decimal_places=2)
    creationDate = models.DateField(auto_now_add=True)
    modificationDate = models.DateField(auto_now=True)

    class Meta:
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add']
        owner_perms = ['inherit', 'change', 'control', 'delete']

    def __str__(self):
        return '{} - {} ({} € HT)'.format(self.batch.title, self.title, self.htAmount)
