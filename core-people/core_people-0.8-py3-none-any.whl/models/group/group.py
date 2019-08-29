from django.db import models

from .group_queryset import GroupQuerySet

class Group(models.Model):
    """
    Represents a Group in the system
    Example: Fly Facillities, Lima
    """
    type        = models.ForeignKey('GroupType', verbose_name ='Type', on_delete=models.CASCADE)
    name        = models.CharField('Name', max_length=200)
    subject     = models.CharField('Subject', max_length=200)
    web         = models.URLField(verbose_name ='Web site', blank=True, null=True)
    people_img  = models.ImageField('People', upload_to="uploads/group/people_img", blank=True, null=True)
    logo_img    = models.ImageField('Thumbnail', upload_to="uploads/group/group_img", blank=True, null=True)
    description = models.TextField('Description', default='', blank=True, null=True)

    members     = models.ManyToManyField('Person', verbose_name = 'Members',through='GroupMembership')
    responsible = models.ForeignKey('Person', related_name ='Head', verbose_name ='Head', blank=True, null=True, on_delete=models.CASCADE)

    objects = GroupQuerySet.as_manager()

    class Meta:
        ordering = ['name',]
        verbose_name = "Group"
        verbose_name_plural = "Groups"

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)

