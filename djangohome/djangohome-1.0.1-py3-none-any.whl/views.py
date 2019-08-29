from django.shortcuts import render
from django.views.generic import View


# Create your homepage views here.
class HomePageView(View):

    def get(self, request, *args, **kwargs):
        template_name = "djangoadmin/djangohome/homepage_view.html"
        return render(request, template_name)