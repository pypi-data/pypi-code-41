from django.db import models

class AuthorAlias(models.Model):

    name   = models.CharField('Alias', max_length=250)  #: Name
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE)