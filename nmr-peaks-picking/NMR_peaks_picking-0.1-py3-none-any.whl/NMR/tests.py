from django.test import TestCase
from sklearn.metrics import classification_report,accuracy_score, confusion_matrix
import os
import django
import csv
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trydjango.settings")
django.setup()
from NMR.models import Spectrum
# Create your tests here.
spectrum = Spectrum.objects.get(pk=2)
print(spectrum.name)
"""
spectrum.csv_file.open(mode="rb")
peakList = spectrum.csv_file.readlines()
spectrum.csv_file.close()
"""
peakList = csv.reader(open(spectrum.csv_file.path, 'r'))
#peakList = peakList[1:]
for row in peakList:
    print(row[0])