from django.core.exceptions import ValidationError
from django.db import models

from permissions.models import Permission

from .publication_queryset import PublicationQuerySet


class PubType(models.Model):
    """
    Represents a Publication type in the system
    Example: Book, Article
    """

    pubtype_id      = models.AutoField(primary_key=True)
    pubtype_name    = models.CharField('Type name', max_length=200)

    class Meta:
        ordering            = ['pubtype_name',]
        verbose_name        = "Publication type"
        verbose_name_plural = "Publications - Types"
        app_label = 'research'

    def __str__(self):
        return self.pubtype_name

    @staticmethod
    def autocomplete_search_fields():
        return ("pubtype_name__icontains",)


class Publication(models.Model):
    """
    Represents a Publication in the system
    Example: Bursting for exploration
    """
    publication_id = models.AutoField(primary_key=True)                     #: ID
    pubtype = models.ForeignKey('PubType', null=True, on_delete=models.SET_NULL) #: Fk to the Publication Type table e.g. article
    publication_keypub = models.NullBooleanField('Is a key publication?')       #: Check box: Is a key publication?
    publication_active = models.NullBooleanField('Sync to website?', help_text='Uncheck this box, if you do not want to turn this publication info public.')            #: Check box: Sync to website?

    publication_year = models.DecimalField('Year', max_digits=4, decimal_places=0)      #: Publication year
    publication_received = models.DateField('Received date', blank=True, null=True,)    #: Recieved Date
    publication_accepted = models.DateField('Accepted date', blank=True, null=True,)    #: Accepted Date
    publication_publish = models.DateField('Publish date', blank=True, null=True,)      #: Published Date
    publication_citations = models.CharField('Citations', max_length=255, blank=True, null=True,)   #: Citations (Hidden field)

    publication_pmid = models.IntegerField('Pubmed id', blank=True, null=True)              #: Pubmed ID e.g. 22929910
    publication_volume = models.CharField('Volume', max_length=30, blank=True, null=True)   #: Volume number e.g. 5
    publication_issue = models.CharField('Issue', max_length=30, blank=True, null=True)     #: Issue number e.g. 9
    publication_pages = models.CharField('Pages', max_length=30, blank=True, null=True)     #: Pages number. e.g 1130-1140
    publication_title = models.CharField('Title', max_length=255)                           #: Title
    publication_abstract = models.TextField('Abstract', blank=True, null=True, default='')  #: Abstract
    publication_web = models.URLField(verbose_name = 'Link', blank=True, null=True)   #: URL to the publication in the web
    publication_authors = models.TextField('Authors', help_text="Write here the authors of the publication. Authors name's should be separated by ','")    #: Authors list
    publication_doi = models.CharField('DOI', max_length=50, blank=True, null=True)                     #: DOI Number e.g. 10.1038/nn.3198
    publication_editors = models.CharField('Editors', max_length=100, blank=True, null=True)            #: Editors (Just for books)
    publication_company = models.CharField('Publishing company', max_length=100, blank=True, null=True) #: Publishing company (Just for books)
    publication_book = models.CharField('Book title', max_length=255, blank=True, null=True)            #: Book title (Just for books)
    publication_file = models.FileField('File', upload_to="uploads/publication/publication_file", blank=True, null=True)   #: Upload the publication file Button

    publication_verified = models.NullBooleanField('This publication was verified by the staff.', default=False)


    journal = models.ForeignKey('Journal', on_delete=models.CASCADE)                                                  #: Fk to the Journal table e.g. Nature
    authors = models.ManyToManyField('people.Person', verbose_name='CNP Authors', help_text='Select the CNP Authors of this publication.')

    objects = PublicationQuerySet.as_manager()

    class Meta:
        verbose_name = "Publication"
        verbose_name_plural = "Publications"
        app_label = 'research'

        permissions = (
            ("app_access_imp_pub", "Access [Import publications] app"),
        )

    def __str__(self):
        return self.publication_title

    def clean(self):
        if self.pk and not self.authors.exists():
            raise ValidationError(
                {'authors': 'You need to assign this Publication to at least one CR member'}
            )
