from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

from .permission_queryset import PermissionQuerySet

class Permission(models.Model):
    """
    Represents a Person's salry Currency in the system
    Example: Euro, Dolar
    """
    permissions_id = models.AutoField(primary_key=True)

    ranking = models.PositiveSmallIntegerField('Rank', default=0)

    djangogroup   = models.ForeignKey('auth.Group',     related_name='rankedpermissions', verbose_name='Django group', on_delete=models.CASCADE)
    researchgroup = models.ForeignKey('people.Group', related_name='rankedpermissions', verbose_name='Research group', blank=True, null=True, on_delete=models.CASCADE)

    objects = PermissionQuerySet.as_manager()

    class Meta:
        ordering = ['djangogroup', 'researchgroup', 'ranking']


    def __str__(self):
        return "<Group: {djangogroup} - Reseach: {researchgroup}>".format(
            researchgroup=self.researchgroup,
            djangogroup=self.djangogroup
        )

    def __list_permissions(self, model):
        contenttype = ContentType.objects.get_for_model(model)
        
        html = "<div class='ui list'>"
        for obj in Permission.objects.filter(content_type=contenttype).order_by('name'):
            if obj in self.djangogroup.permissions.all():
                icon = "check circle green"
            else:
                icon = "times circle red"
            html += "<div class='item'><i class='{}  icon'></i>{}</div>".format(icon, obj.name)
        html += '</div>'

        return html


    @property
    def order(self):
        try:
            from orders.models import Order
            return self.__list_permissions(Order)
        except:
            return None

    @property
    def proposal(self):
        try:
            from humanresources.models import ContractProposal
            return self.__list_permissions(ContractProposal)
        except:
            return None

    @property
    def contract(self):
        try:
            from humanresources.models import Contract
            return self.__list_permissions(Contract)
        except:
            return None

    @property
    def person(self):
        try:
            from people.models import Person
            return self.__list_permissions(Person)
        except:
            return None

    @property
    def publication(self):
        try:
            from research.models import Publication
            return self.__list_permissions(Publication)
        except:
            return None
    