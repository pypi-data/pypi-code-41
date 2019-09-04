# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse
from django.conf import settings
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q, Sum, Count
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

from .models import Classify, Topic, TopicImage
from .forms import ClassifyForm, TopicForm, TopicSearchForm, TopicImageForm

User = get_user_model()


# Create your views here.
def test(request):
    return


# ========Classify==========
class ClassifyList(ListView):
    model = Classify
    template_name = 'bee_django_wiki/classify/list.html'
    context_object_name = 'classify_list'
    paginate_by = 20


class ClassifyCreate(CreateView):
    model = Classify
    form_class = ClassifyForm
    template_name = 'bee_django_wiki/classify/form.html'
    success_url = reverse_lazy("bee_django_wiki:classify_list")


class ClassifyUpdate(UpdateView):
    model = Classify
    form_class = ClassifyForm
    template_name = 'bee_django_wiki/classify/form.html'
    success_url = reverse_lazy("bee_django_wiki:classify_list")


class ClassifyDelete(DeleteView):
    model = Classify
    success_url = reverse_lazy('bee_django_wiki:classify_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


# ========Topic==========
class TopicList(ListView):
    model = Topic
    template_name = 'bee_django_wiki/topic/list.html'
    context_object_name = 'topic_list'
    paginate_by = 20

    def get_queryset(self):
        name = self.request.GET.get("name")
        classify_id = self.request.GET.get("classify_id")
        if self.request.user.has_perm("bee_django_wiki.view_all_topic"):
            queryset = Topic.objects.all()
        else:
            group_list = self.request.user.groups.all()
            queryset = Topic.objects.filter(view_group__topic__view_group__in=group_list).distinct()
        if not name in [None]:
            queryset = queryset.filter((Q(title__icontains=name) | Q(tag__icontains=name)))
        if not classify_id in [0, "0", None]:
            queryset = queryset.filter(classify_id=classify_id)
        return queryset

    # def search(self):
    #     name = self.request.GET.get("name")
    #     if not name in [None]:
    #         self.queryset =self.queryset.filter((Q(title__icontains=name) | Q(tag__icontains=name)))
    #     return self.queryset

    def get_context_data(self, **kwargs):
        context = super(TopicList, self).get_context_data(**kwargs)
        name = self.request.GET.get("name")
        context['search_form'] = TopicSearchForm({"name": name})
        context['classify_list'] = Classify.objects.all()
        return context


class TopicDetail(DetailView):
    model = Topic
    template_name = 'bee_django_wiki/topic/detail.html'
    context_object_name = 'topic'

    def get_object(self, queryset=None):
        if self.request.user.has_perm("bee_django_wiki.view_all_topic"):
            return Topic.objects.get(id=self.kwargs["pk"])
        else:
            group_list = self.request.user.groups.all()
            try:
                topic = Topic.objects.get(view_group__in=group_list, id=self.kwargs["pk"])
                return topic
            except:
                return None

        # return

    def get_context_data(self, **kwargs):
        context = super(TopicDetail, self).get_context_data(**kwargs)
        context['classify_list'] = Classify.objects.all()
        return context


class TopicCreate(CreateView):
    model = Topic
    form_class = TopicForm
    template_name = 'bee_django_wiki/topic/form.html'
    success_url = reverse_lazy("bee_django_wiki:topic_list")


class TopicUpdate(UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = 'bee_django_wiki/topic/form.html'
    success_url = reverse_lazy("bee_django_wiki:topic_list")

    def get_success_url(self):
        return reverse_lazy("bee_django_wiki:topic_detail", kwargs=self.kwargs)


class TopicDelete(DeleteView):
    model = Topic
    success_url = reverse_lazy('bee_django_wiki:topic_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


@csrf_exempt
def upload_image(request):
    # 默认上传图片大小为2M
    if hasattr(settings, "WIKI_TOPIC_UPLOAD_MAXSIZE"):
        _max_size = settings.WIKI_TOPIC_UPLOAD_MAXSIZE
    else:
        _max_size = 2
    max_size = _max_size * 1024 * 1024
    if request.method == "POST":
        file = request.FILES.get('image')
        if file.size > max_size:
            return HttpResponse("error|图片大小不能超过" + _max_size.__str__() + "M!")

        # 保存图片。用户上传的图片，与用户的对应关系也保存到数据库中
        form = TopicImageForm(request.POST, request.FILES)
        if form.is_valid():
            topic_image = form.save(commit=True)
            return HttpResponse(topic_image.image.url)
        else:
            print(form.errors)
            return HttpResponse("error|文件存储错误")
    else:
        return HttpResponse("error|请求错误")
