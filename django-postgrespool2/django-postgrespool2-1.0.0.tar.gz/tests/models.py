from django.db import models


class DogModel(models.Model):

    name = models.CharField(max_length=200)
