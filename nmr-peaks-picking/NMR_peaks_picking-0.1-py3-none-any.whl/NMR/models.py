from django.db import models
import re
from django.urls import reverse
from .validators import validate_zip_file, validate_tsv_file


# spectra table
class Spectrum(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default='')
    # number of peaks
    quantity = models.IntegerField(default=700, blank=True, null=True)
    # spectrum data
    spectrum_file = models.FileField(blank=True, upload_to="spectrum/", help_text='Spectrum data', validators=[validate_zip_file])
    # peaks data
    peaks_tsv_file = models.FileField(blank=True, null=True, upload_to="spectrum/", help_text='Peak data', validators=[validate_tsv_file])
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name

    # count the number of labeled peaks
    def count_peak(self):
        count = 0
        for peak in self.peak_set.all():
            if peak.isPeak:
                count += 1
        return count

    # display peaks
    def get_absolute_url(self):
        """Returns the url to access a particular instance of MyModelName."""
        return reverse('peak', args=[str(self.id)])


class Peak(models.Model):
    spectrum = models.ForeignKey(Spectrum, on_delete=models.CASCADE)
    pid = models.IntegerField(default=0)
    # composed of spectrum.id + 0 + pid, for example: 101 for fixed area and 102 larger
    id = models.CharField(primary_key=True, max_length=100)
    # label being peak or not
    isPeak = models.BooleanField(default=False)
    # prediction as peak or not
    predict = models.BooleanField(default=False)
    # probability of being peak
    probability = models.IntegerField(default=0)
    # plotting image
    plot = models.ImageField(blank=True, upload_to="peak/")
    # indexes
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    # chemical shift
    x_ppm = models.DecimalField(default=0, max_digits=20, decimal_places=4)
    y_ppm = models.DecimalField(default=0, max_digits=20, decimal_places=4)
    # range
    x0 = models.IntegerField(default=0)
    x1 = models.IntegerField(default=0)
    y0 = models.IntegerField(default=0)
    y1 = models.IntegerField(default=0)

    # ordering peaks by probability and id
    class Meta:
        ordering = ('-probability', 'id')

    # delete peak image if peak data deleted or modified
    def save(self, *args, **kwargs):
        # delete old file when replacing by updating the file
        try:
            this = Peak.objects.get(id=self.id)
            if this.plot != self.plot:
                this.plot.delete(save=False)
        except:
            pass  # when new photo then we do nothing, normal case
        super(Peak, self).save(*args, **kwargs)

    def __int__(self):
        return self.id

    # return the larger box for smaller box, and vise versa
    def get_the_other(self):
        if int(self.id) % 2 == 0:
            return Peak.objects.get(id=str(self.spectrum.id)+str(0)+str(self.pid*2-1))
        else:
            return Peak.objects.get(id=str(self.spectrum.id)+str(0)+str(self.pid*2))
