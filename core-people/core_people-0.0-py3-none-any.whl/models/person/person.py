import warnings, os
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from django.utils.html import format_html
from django.utils.text import slugify
from sorl.thumbnail import get_thumbnail
from django.utils    import timezone

from .person_queryset import PersonQuerySet

def get_image_upload_path(instance, filename):
    return os.path.join('uploads', 'person', 'img', str(instance.pk), filename)

def get_cv_upload_path(instance, filename):
    return os.path.join('uploads', 'person', 'cv', str(instance.pk), filename)

class Person(models.Model):
    """
    Represents a Person in the system
    Example: Adam Kampff, Ana Elias
    """
    DEFAULT_PICTURE_URL = '/static/square-image.png'

    active = models.BooleanField('Active', default=True)

    birthday    = models.DateField('Birthday', blank=True, null=True, )
    gender      = models.CharField('Gender', max_length=1, choices=(('F', 'Female'), ('M', 'Male')))
    first_name  = models.CharField('First name', max_length=40, help_text='This field will appear in the website.')
    middle_name = models.CharField('Middle name', max_length=100, blank=True)
    last_name   = models.CharField('Last name', max_length=40, help_text='This field will appear in the website.')
    full_name   = models.CharField('Name', max_length=150)

    email = models.EmailField('Research email', help_text='This field will appear in the website.')
    web   = models.URLField('Website', blank=True, null=True,
                          help_text='This field will appear in the website.')
    personal_email  = models.EmailField('Personal email', blank=True, null=True)
    phone_extension = models.IntegerField('Phone extension', blank=True, null=True)
    phone_number    = models.CharField('Contact', max_length=20, blank=True, null=True,
                                    help_text='This field will appear in the website if the next field is checked.')
    emergency_contact = models.TextField('Emergency contacts', max_length=100, blank=True, null=True, default='')

    biography        = models.TextField('Biography', blank=True, null=True, default='',
                                        help_text='This field will appear in the website.')
    curriculum_vitae = models.FileField('Short Vitae', upload_to=get_cv_upload_path, blank=True, null=True,
                                        help_text='This field will appear in the website.')

    position    = models.ForeignKey('Position', blank=True, null=True, on_delete=models.CASCADE)
    img         = models.ImageField(upload_to=get_image_upload_path, max_length=150, blank=True, verbose_name='Picture', help_text='This field will appear in the website.')  #: Picture link
    room        = models.CharField('Room', max_length=10, blank=True, null=True)     #: Room Number
    card_number = models.IntegerField('Card number', blank=True, null=True)
    date_joined = models.DateField('Joined date', blank=True, null=True, )
    date_left   = models.DateField('Leave date', blank=True, null=True, )

    auth_user   = models.OneToOneField(
        'auth.User',
        blank=True, null=True, verbose_name='User', related_name='person',
        on_delete=models.SET_NULL
    )

    objects = PersonQuerySet.as_manager()

    class Meta:
        ordering = ['first_name','last_name' ]
        verbose_name = "Person"
        verbose_name_plural = "People"

        permissions = (
            ("app_access_hr",  "Access [Human Resources] app"),
            ("app_access_people", "Access [People] app"),
        )

    def __str__(self):
        return self.name


    def save(self, *args, **kw):
        """
        the function will create a django user for new person added to
        the data base or for each person that has been changed/saved
        without a django user

        the function will only feed the first name, last name and email
        as feeded in the person data base, and will create auser name
        first name.last name

        the administrator will have to provide a password, permmissions
        and related group in order to give acssess to this user
        """
        if self.auth_user is None:
            if User.objects.filter(email=self.email).exists():
                #if there is a user in django with this email
                self.auth_user = User.objects.get(email=self.email)
            else:
                self.auth_user = User.objects.create_user(
                    ".".join(list(map(slugify, [self.first_name, self.last_name]))),
                    self.email,
                    last_login=timezone.now()
                )
            self.auth_user.is_active = True
            self.auth_user.is_staff  = True
            self.auth_user.first_name = self.first_name
            self.auth_user.last_name  = self.last_name
            self.auth_user.save()

            # Set the email as verified automatically
            if EmailAddress.objects.filter(email=self.auth_user.email, user=self.auth_user).exists():
                e = EmailAddress(user=self.auth_user, email=self.auth_user.email, verified=True, primary=True)
                e.save()

        # TODO the above code block needs testing and updating
        # TODO create method .join_guest_group() to reuse

        if self.active:
            self.auth_user.is_active = True
        else:
            # If Person is set as inactive, revoke all access permissions
            self.auth_user.is_active = False
            self.auth_user.is_staff  = False
            self.auth_user.is_superuser = False
            self.auth_user.user_permissions.clear()
            self.auth_user.groups.clear()
        # The active status can be reverted but permissions will require
        # manual assignment
        self.auth_user.save()

        super().save(*args, **kw)


    @staticmethod
    def autocomplete_search_fields():
        return ("first_name__icontains", "middle_name__icontains", 'last_name__icontains')

    def fullname(self):
        """To be deprecated in favour of `full_name` field."""
        warnings.warn(
            'Stop using fullname() method, use the full_name field instead',
            DeprecationWarning,
        )
        return self.full_name

    @property
    def name(self):
        return " ".join(filter(None, (self.first_name, self.last_name)))

    def get_privateinfo(self):
        from humanresources.models import PrivateInfo

        try:
            pinfo = self.privateinfo
        except PrivateInfo.DoesNotExist:
            pinfo = PrivateInfo(person=self)
            pinfo.save()

        return pinfo


    def personprivateinfo(self):
        """
        Return a link "Go" to the "Private info" page where a user with permission
        can read and edit the private information of the selected person.
        If this person still dont have private information, the function
        returns a "Not created yet" label.

        @type  self:    Person
        @rtype:         link
        @return:        link to the "Private info" page of that person
        """
        from humanresources.models import PrivateInfo
        try:
            private = PrivateInfo.objects.get(person=self)
            return format_html("""<a class='btn btn-warning' href='/humanresources/privateinfo/{0}/' ><i class="icon-lock icon-black"></i> Show private info</a>""".format(str(private.privateinfo_id)))
        except ObjectDoesNotExist:
            return format_html("""<a class='btn btn-warning' href='/humanresources/privateinfo/add/?person={0}' ><i class="icon-lock icon-black"></i> Private info</a>""".format(str(self.pk)))

    personprivateinfo.short_description = 'Private info'
    personprivateinfo.allow_tags = True

    def person_contracts(self):
        """
        Return a link "Contracts" to the "Contracts" page where a user with permission
        can read and edit the contracts of the selected person.
        If this person still dont have a contract, the function
        returns a "Not created yet" label.

        @type  self:    Person
        @rtype:         link
        @return:        link to the "contracts" page of that person
        """
        try:
            return format_html("""<a class="btn btn-warning" href='/humanresources/contract/?person_id=%s' ><i class="icon-folder-close icon-black"></i> Show contracts</a>""" % (self.pk))
        except ObjectDoesNotExist:
            return "Not created yet"
    person_contracts.short_description = 'Contracts'
    person_contracts.allow_tags = True

    def has_active_contract(self):
        """Returns True if at least one of its contracts is active."""
        return self.contract_set.active().exists()

    def get_groups(self):
        """
        Returns a string with the name of all Research Groups this
        Person is a member of.
        """
        return '; '.join([
            membership.group.name
            for membership in self.groupmembership_set.active().all()
        ])

    def thumbnail_url(self, geometry_string):
        if self.img:
            url = get_thumbnail(
                self.img,
                geometry_string,
                crop='center',
                format='PNG',
            ).url
        else:
            url = self.DEFAULT_PICTURE_URL
        return url

    def thumbnail_80x80(self):
        url = self.thumbnail_url(geometry_string='80x80')
        return "<img class='ui top aligned tiny image rounded' src='{url}''>".format(url=url)
    thumbnail_80x80.short_description = ' '

    def photo(self):
        if self.img:
            return format_html("""<a class='imageLink' target='_blank'href='%s'><img src='%s' width='50px' height='50px'  ></a>""" % (self.img.url, self.img.url))
        else:
            return ''
    photo.short_description = 'Picture'
    photo.allow_tags = True

    # Object Permissions

    def has_view_permission(self, user):
        if any((
            user.is_superuser,
            user == self.auth_user,
            user.groups.filter(name=settings.PROFILE_HUMAN_RESOURCES).exists(),
        )):
            return True
        else:
            return False

    def has_change_permission(self, user):
        if any((
            user.is_superuser,
            user == self.auth_user,
            user.groups.filter(name=settings.PROFILE_HUMAN_RESOURCES).exists(),
        )):
            return True
        else:
            return False

    ######################################################################################
    #### FILTERS #########################################################################
    ######################################################################################


