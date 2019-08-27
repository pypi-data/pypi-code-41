from django.db import models

class InstitutionAffiliation(models.Model):
    """
    Represents a Person wich is a Member of that Group
    """
    person = models.ForeignKey(
        to='Person',
        related_name='membership',
        on_delete=models.CASCADE,
    )

    institution = models.ForeignKey(
        to='common.Institution',
        related_name='membership',
        on_delete=models.CASCADE,
    )

    date_joined = models.DateField('Joined', null=True, blank=True)
    date_left = models.DateField('Left', null=True, blank=True)
