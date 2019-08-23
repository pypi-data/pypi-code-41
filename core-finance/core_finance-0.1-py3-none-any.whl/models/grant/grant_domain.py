from django.db import models

class Grantdomain(models.Model):
    """
    Represents a Grant domain in the system
    Example: public, private
    """
    domain = models.CharField('Grant domain', max_length=200)

    class Meta:
        verbose_name = "Grant domain"
        verbose_name_plural = "Grant domains"

    def __str__(self):
        return self.domain


