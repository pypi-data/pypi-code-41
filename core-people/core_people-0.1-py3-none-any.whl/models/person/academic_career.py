from django.db import models

class AcademicCareer(models.Model):
    """
    Represents an Academic Career of a Person in the system
    """
    graduation_year = models.IntegerField(null=True)
    person = models.ForeignKey('people.Person', on_delete=models.CASCADE, )

    institution = models.ForeignKey(
        to='common.Institution',
        verbose_name='Institute',  # aka academic institution
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    degree = models.ForeignKey(
        to='Degree',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    field_of_study = models.ForeignKey(
        to='ScientificArea',
        verbose_name='Field of Study',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ['-graduation_year']
        verbose_name = "Academic Career"
        verbose_name_plural = "Academic Careers"

    def __str__(self):
        if not self.degree or not self.field_of_study:
            return f'Incomplete Academic record for {self.person}'
        else:
            return f'{self.person} is a {self.degree} in {self.field_of_study}'
