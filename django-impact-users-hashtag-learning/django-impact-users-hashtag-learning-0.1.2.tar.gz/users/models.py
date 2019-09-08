from django.contrib.auth.models import AbstractUser, UserManager, BaseUserManager
from django.db.models import CharField, ForeignKey, CASCADE, ManyToManyField, BooleanField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver

from schools.models import School, Faculty

class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            username,
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def count_faculty_members(self, faculty):
        return self.get_faculty_members(faculty).count()

    def get_faculty_members(self, faculty):
        return self.filter(
            member_of_faculties=faculty
        )

    def update_dont_show_help(self, dont_show_help, user):

        if dont_show_help is True:
            user.show_overview_help = False
            user.save()

class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)

    school = ForeignKey(School, on_delete=CASCADE, blank=True, null=True)
    faculty = ForeignKey(Faculty, on_delete=CASCADE, blank=True, null=True)
    member_of_faculties = ManyToManyField(Faculty, related_name='faculty_membership', blank=True)
    school_admin = BooleanField(default=True)
    show_overview_help = BooleanField(default=True)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def get_school(self):
        return self.school

    def get_faculty(self):
        return self.faculty

    def is_departmental(self):
        if self.faculty.faculty_name == 'School':
            return False
        else:
            return True

    def get_user_department_membership(self):
        return self.member_of_faculties.all()

    def count_user_department_membership(self):
        return self.member_of_faculties.all().count()

    objects = CustomUserManager()

@receiver(pre_save, sender=User)
def update_username_from_email(sender, instance, **kwargs):
    user_email = instance.email
    username = user_email
    instance.username = username