from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from trydjango.settings import MEDIA_ROOT
from django.urls import reverse
from django.views import generic
from .models import Spectrum, Peak
from .process import processing, find_peak, plot
from .svm import SVM, pred
import nmrglue as ng
import csv
import os
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


# add spectrum data form
class SpectrumCreate(CreateView):
    model = Spectrum
    fields = '__all__'
    success_url = reverse_lazy('index')

    # turn 'quantity' and 'peaks_tsv_file' to optional field
    def get_form(self, form_class=None):
        form = super(SpectrumCreate, self).get_form(form_class)
        form.fields['quantity'].required = False
        form.fields['peaks_tsv_file'].required = False
        return form

    # save the uploaded file to database
    def form_valid(self, form):
        self.object = Spectrum(spectrum_file=self.get_form_kwargs().get('files')['spectrum_file'])
        if self.get_form_kwargs().get('peaks_tsv_file'):
            self.object = Spectrum(csv_file=self.get_form_kwargs().get('files')['peaks_tsv_file'])
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


# update spectrum data form
class SpectrumUpdate(UpdateView):
    model = Spectrum
    fields = '__all__'
    success_url = reverse_lazy('index')


# delete spectrum data form
class SpectrumDelete(DeleteView):
    model = Spectrum
    success_url = reverse_lazy('spectra')


# spectra list
class SpectrumListView(generic.ListView):
    model = Spectrum
    context_object_name = 'my_spectrum_list'
    queryset = Spectrum.objects.all()
    template_name = 'NMR/spectrum.html'


# home page
def index(request):
    # order spectra by id
    spectrum_list = Spectrum.objects.order_by('id')
    # session data for visit times
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    context = {
        'spectrum_list': spectrum_list,
        'num_visits': num_visits,
    }
    return render(request, 'NMR/index.html', context)


# process spectrum data to generate peaks
def process(request, spectrum_id):
    spectrum = get_object_or_404(Spectrum, pk=spectrum_id)
    dic, data, baseline = processing(spectrum)
    # define the fixed size of peak
    x_pad = 20
    y_pad = 7
    id = 0
    # get unit transform data
    udic = ng.bruker.guess_udic(dic, data)
    ucf0 = ng.fileiobase.uc_from_udic(udic, dim=0)
    ucf1 = ng.fileiobase.uc_from_udic(udic, dim=1)
    # no tsv file for peaks uploaded
    if not spectrum.peaks_tsv_file:
        # find user-defined number of peaks by maxima selection
        peakList = find_peak(data, baseline, spectrum.quantity)
        # create two boxes for each peak
        for [y, x] in peakList:
            id += 2
            plot(spectrum, x, y, id, baseline, data, ucf0, ucf1, x_pad, y_pad)
    # tsv file for peaks uploaded
    else:
        # read in chemical shift foe peaks
        peakList = csv.reader(open(spectrum.peaks_tsv_file.path, 'r'), delimiter='\t')
        try:
            firstline = True
            for row in peakList:
                if firstline:  # skip first line
                    firstline = False
                    continue
                # transform from ppm to index
                y = ucf0(float(row[1]), "ppm")
                x = ucf1(float(row[0]), "ppm")
                id += 2
                peak = plot(spectrum, x, y, id, baseline, data, float(row[0]), float(row[1]), x_pad, y_pad)
                # extract peak label
                peak.isPeak = row[2].strip().lower() in ("yes", "true", "1")
                peak.save()
        # if axes flipped
        except IndexError:
            firstline = True
            for row in peakList:
                if firstline:  # skip first line
                    firstline = False
                    continue
                # transform from ppm to index
                y = ucf0(float(row[0]), "ppm")
                x = ucf1(float(row[1]), "ppm")
                id += 2
                peak = plot(spectrum, x, y, id, baseline, data, float(row[0]), float(row[1]), x_pad, y_pad)
                # extract peak label
                peak.isPeak = row[2].strip().lower() in ("yes", "true", "1")
                peak.save()
    return render(request, 'NMR/process.html', {'spectrum': spectrum})


# display peaks for picking
def detail(request, spectrum_id):
    spectrum = get_object_or_404(Spectrum, pk=spectrum_id)
    return render(request, 'NMR/detail.html', {'spectrum': spectrum})


# peak picking page
def pick(request, spectrum_id):
    spectrum = get_object_or_404(Spectrum, pk=spectrum_id)
    try:
        # get the list of chosen peak id
        peak_list = request.POST.getlist('tick')
    except (KeyError, Peak.DoesNotExist):
        # Redisplay the question picking form.
        return render(request, 'NMR/detail.html', {
            'spectrum': spectrum,
            'error_message': "You didn't select a peak.",
        })
    else:
        # flip the peak label for chosen peaks
        for chosen_peak in peak_list:
            selected_peak = spectrum.peak_set.get(pk=chosen_peak)
            selected_peak.isPeak = not selected_peak.isPeak
            selected_peak.save()
        return HttpResponseRedirect(reverse('index'))


# support vector machine
def svm(request):
    list = request.POST.getlist('train')
    spectrum_list = Spectrum.objects.filter(pk__in=list)
    accuracy_train, accuracy_test, tn, fp, fn, tp = 0, 0, 0, 0, 0, 0
    if spectrum_list.count() > 0:
        accuracy_train, accuracy_test, tn, fp, fn, tp = SVM(spectrum_list)
    context = {
        'accuracy_train': accuracy_train,
        'accuracy_test': accuracy_test,
        'tn': tn,
        'fp': fp,
        'fn': fn,
        'tp': tp,
        'spectrum_list': spectrum_list
    }
    return render(request, 'NMR/svm.html', context)


# change the isPeak labels
def change(request):
    list = request.POST.getlist('change')
    peak_list = Peak.objects.filter(pk__in=list)
    for chosen_peak in peak_list:
        chosen_peak.isPeak = not chosen_peak.isPeak
        chosen_peak.save()
    context = {'peak_list': peak_list}
    return render(request, 'NMR/results.html', context)


# use model to predict and display in three tables according to the probability
def predict(request, spectrum_id):
    spectrum = get_object_or_404(Spectrum, pk=spectrum_id)
    file = "train_model.m"
    MODEL_ROOT = os.path.join(MEDIA_ROOT, 'model')
    path = os.path.join(MODEL_ROOT, file)
    # check model existence
    if os.path.isfile(path):
        accuracy, tn, fp, fn, tp = pred(spectrum, path)
        count = 0
        high_peak = []
        middle_peak = []
        low_peak = []
        for peak in spectrum.peak_set.all():
            if int(peak.id) % 2 != 0 and 70 <= peak.probability:
                high_peak.append(peak)
            elif int(peak.id) % 2 != 0 and 30 <= peak.probability < 70:
                middle_peak.append(peak)
                count += 1
            elif int(peak.id) % 2 != 0 and peak.probability < 30:
                low_peak.append(peak)
            else:
                continue
    else:
        high_peak, middle_peak, low_peak, count = False, False, False, 0
        accuracy, tn, fp, fn, tp = -1, -1, -1, -1, -1
    context = {
        'spectrum': spectrum,
        'high_peak': high_peak,
        'middle_peak': middle_peak,
        'low_peak': low_peak,
        'count': count,
        'accuracy': accuracy,
        'tn': tn,
        'fp': fp,
        'fn': fn,
        'tp': tp,
    }
    return render(request, 'NMR/predict.html', context)


# save the prediction results and user modifications
def save(request, spectrum_id):
    spectrum = get_object_or_404(Spectrum, pk=spectrum_id)
    list = request.POST.getlist('tick')
    peak_list = Peak.objects.filter(pk__in=list)
    for peak in spectrum.peak_set.all():
        peak.isPeak = peak.predict
        peak.save()
    for chosen_peak in peak_list:
        chosen_peak.isPeak = not chosen_peak.isPeak
        chosen_peak.save()
    context = {'peak_list': peak_list}
    return render(request, 'NMR/results.html', context)


# display peak and non_peak table for spectrum
def peak(request, spectrum_id):
    spectrum = get_object_or_404(Spectrum, pk=spectrum_id)
    count = 0
    non_count = 0
    peak_list = []
    non_peak_list = []
    for peak in spectrum.peak_set.all():
        if int(peak.id) % 2 != 0 and peak.isPeak:
            peak_list.append(peak)
            count += 1
        elif int(peak.id) % 2 != 0 and peak.isPeak is False:
            non_peak_list.append(peak)
            non_count += 1
        else:
            continue
    context = {
        'spectrum': spectrum,
        'count': count,
        'non_count': non_count,
        'peak_list': peak_list,
        'non_peak_list': non_peak_list
    }
    return render(request, 'NMR/peak.html', context)


# show the peaks labels just been changed
def results(request):
    return render(request, 'NMR/results.html')


# return tsv file of peaks for spectrum
def csv_file(request, spectrum_id):
    spectrum = get_object_or_404(Spectrum, pk=spectrum_id)
    response = HttpResponse(content_type='text/tsv')
    response['Content-Disposition'] = 'attachment;filename=peak_list.tsv'
    writer = csv.writer(response, delimiter='\t')
    count = 0
    for peak in spectrum.peak_set.all():
        if int(peak.id) % 2 != 0 and peak.isPeak:
            count += 1
            writer.writerow([count, peak.y_ppm, peak.x_ppm])
        else:
            continue
    return response




