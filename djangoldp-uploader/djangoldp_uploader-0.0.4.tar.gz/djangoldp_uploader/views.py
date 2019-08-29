from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from djangoldp_uploader.forms import DocumentForm
from djangoldp_uploader.models import Document


def home(request):
    documents = Document.objects.all()
    return render(request, 'home.html', { 'documents': documents })


def demo_sib(request):
    return render(request, 'demo_sib.html')


def upload(request):
    file_obj = request.FILES['file']
    fs = FileSystemStorage()
    filename = fs.save(file_obj.name, file_obj)
    uploaded_file_url = fs.url(filename)
    return uploaded_file_url


class FileUploadView(APIView):
    def post(self, request):
        if request.method == 'POST' and request.FILES['file']:
            uploaded_file_url = upload(request)
            response = Response(status=204, headers={'Location': "{}{}".format(settings.SITE_URL, uploaded_file_url)})
            response["Access-Control-Allow-Origin"] = request.META.get('HTTP_ORIGIN')
            response["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE"
            response["Access-Control-Allow-Headers"] = "authorization, Content-Type, if-match, accept"
            response["Access-Control-Expose-Headers"] = "Location"
            response["Access-Control-Allow-Credentials"] = 'true'
            
            return response


def upload_view(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file_url = upload(request)
        return render(request, 'simple_upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'simple_upload.html')


def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = DocumentForm()
    return render(request, 'model_form_upload.html', {
        'form': form
    })
