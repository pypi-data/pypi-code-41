from django.db import models





class Journal(models.Model):
    """
    Represents a Journal 
    Example: Cell, Nature
    """

    journal_id = models.AutoField(primary_key=True)         #: ID                      
    journal_name = models.CharField('Name', max_length=250) #: Name
    journal_publisher = models.CharField('Publisher', max_length=80, blank=True, null=True) #: Publisher name
    journal_abbreve = models.CharField('Short name', max_length=80)                 #: Short name of the Journal e.g. Cell
    journal_issn = models.CharField('ISSN', max_length=15, blank=True, null=True)   #: ISSN Number of the Journal e.g. 0092-8674
    journal_essn = models.CharField('ESSN', max_length=15, blank=True, null=True)   #: ESSN Number of the Journal e.g. 1097-4172

    class Meta:
        ordering = ['journal_name',]
        verbose_name = "Research Journal"
        verbose_name_plural = "Research Journals"
        app_label = 'research'

    def __str__(self):
        return self.journal_name

    @staticmethod
    def autocomplete_search_fields():
        return ("journal_name__icontains", "journal_publisher__icontains", 'journal_abbreve__icontains')


class JournalImpactFactor(models.Model):
    """
    Represents a Journal Impact Factor
    Example: Cell, Nature
    Hidden Table???
    """

    journalif_id = models.AutoField(primary_key=True)   #: ID
    jornal = models.ForeignKey(Journal, on_delete=models.CASCADE)                 #: Fk to the Journal table
    journalif_year = models.IntegerField('Year')        #: Year
    journalif_value = models.DecimalField('Impact factor value', max_digits=6, decimal_places=3)    #: Impact Factor value

    class Meta:
        ordering = ['journalif_year',]
        verbose_name = "Journal Impact Factor"
        verbose_name_plural = "Journals Impact Factors"
        app_label = 'research'

    def __str__(self):
        return "%s | year: %d => %f" % (self.journal, self.journalif_year, self.journalif_value)



class JournalAlias(models.Model):

    name    = models.CharField('Alias', max_length=250) #: Name
    journal = models.ForeignKey('Journal', on_delete=models.CASCADE)