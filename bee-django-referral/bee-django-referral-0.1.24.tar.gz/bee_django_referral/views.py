# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json, qrcode, os, shutil, urllib
from django.shortcuts import get_object_or_404, reverse, redirect, render
from django.views.generic import ListView, DetailView, TemplateView, RedirectView
from django.db.models import Q, Sum, Count
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.utils.datastructures import MultiValueDict
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.utils.six import BytesIO
from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django import forms
from django.utils import timezone

from .decorators import cls_decorator, func_decorator
from .models import Activity, UserActivity, UserShareImage
from .utils import create_qrcode_timestamp
from .forms import ActivityForm, ActivityUpdateForm, ActivityQrCodeImgUpdateForm, ActivityQrCodeUpdateForm, \
    UserActivityForm
from .qr import create_qrcode, merge_img, toRgb

# from .exports import get_user_qrcode, create_user_image, get_user_qrcode_image

User = get_user_model()


# Create your views here.

def test(request):
    UserShareImage().fix_qrcode()
    return


class UserQrcodeStatus:
    user_qrcode_image_status_unused = 1
    user_qrcode_image_status_reg = 2
    user_qrcode_image_status_pay = 4

    user_qrcode_image_status_choices = (
        (user_qrcode_image_status_unused, '未使用'),
        (user_qrcode_image_status_reg, '已注册'),
        (user_qrcode_image_status_pay, '已缴费'),
    )


# ========Activity===========
@method_decorator(cls_decorator(cls_name='ActivityList'), name='dispatch')
class ActivityList(ListView):
    model = Activity
    template_name = 'bee_django_referral/activity/activity_list.html'
    context_object_name = 'activity_list'
    paginate_by = 20
    ordering = ["-start_date"]


@method_decorator(cls_decorator(cls_name='ActivityDetail'), name='dispatch')
class ActivityDetail(DeleteView):
    model = Activity
    template_name = 'bee_django_referral/activity/activity_detail.html'
    context_object_name = 'activity'


@method_decorator(cls_decorator(cls_name='SourceCreate'), name='dispatch')
class ActivityCreate(CreateView):
    model = Activity
    form_class = ActivityForm
    template_name = 'bee_django_referral/activity/activity_form.html'


@method_decorator(cls_decorator(cls_name='ActivityUpdate'), name='dispatch')
class ActivityUpdate(UpdateView):
    model = Activity
    form_class = ActivityUpdateForm
    template_name = 'bee_django_referral/activity/activity_form.html'

    # def get_context_data(self, **kwargs):
    #     context = super(ActivityUpdate, self).get_context_data(**kwargs)
    #     context["activity"] = Activity.objects.get(id=self.kwargs["pk"])
    #     return context


@method_decorator(cls_decorator(cls_name='ActivityQrcodeUpload'), name='dispatch')
class ActivityQrcodeUpload(UpdateView):
    model = Activity
    form_class = ActivityQrCodeImgUpdateForm
    template_name = 'bee_django_referral/activity/activity_qrcode_upload_form.html'

    def get_success_url(self):
        return reverse_lazy('bee_django_referral:activity_qrcode_update', kwargs=self.kwargs)


@method_decorator(cls_decorator(cls_name='ActivityQrcodeUpdate'), name='dispatch')
class ActivityQrcodeUpdate(UpdateView):
    model = Activity
    form_class = ActivityQrCodeUpdateForm
    template_name = 'bee_django_referral/activity/activity_qrcode_form.html'

    def get_success_url(self):
        return reverse_lazy('bee_django_referral:activity_qrcode_update', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super(ActivityQrcodeUpdate, self).get_context_data(**kwargs)
        # context["img_form"] = ActivityQrCodeImgUpdateForm
        context["timestamp"] = create_qrcode_timestamp().__str__()
        return context

    def form_valid(self, form):
        #     # This method is called when valid form data has been POSTed.
        #     # It should return an HttpResponse.
        activity = form.save(commit=True)
        ret = activity.create_qrcode_img()
        if ret:
            activity.qrcode_thumb = ret
            activity.save()
        return super(ActivityQrcodeUpdate, self).form_valid(form)


class ActivityQrcodeInvaild(TemplateView):
    template_name = 'bee_django_referral/custom_user/activity_qrcode_invaild.html'

    def get_context_data(self, **kwargs):
        context = super(ActivityQrcodeInvaild, self).get_context_data(**kwargs)
        errcode = self.request.GET.get("errcode")
        errmsg = UserShareImage.get_qrcode_errmsg(errcode)
        context['errmsg'] = errmsg
        return context


# =======User Activity =======

class UserActivityCreate(CreateView):
    model = UserActivity
    form_class = UserActivityForm
    template_name = 'bee_django_referral/user/activity/form.html'

    def get_success_url(self):
        return reverse_lazy('bee_django_referral:user_activity_list', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserActivityCreate, self).get_context_data(**kwargs)
        user = User.objects.get(id=self.kwargs["user_id"])
        context["user"] = user
        return context

    def form_valid(self, form):
        #     # This method is called when valid form data has been POSTed.
        #     # It should return an HttpResponse.
        user_activity = form.save(commit=False)
        user = User.objects.get(id=self.kwargs["user_id"])
        user_activity.user = user
        user_activity.save()
        return super(UserActivityCreate, self).form_valid(form)


class UserActivityList(TemplateView):
    template_name = 'bee_django_referral/user/activity/list.html'

    def get_context_data(self, **kwargs):
        context = super(UserActivityList, self).get_context_data(**kwargs)
        user = User.objects.get(id=self.kwargs["user_id"])
        context["user"] = user
        activity_list = Activity.objects.filter(show_type=1)
        user_activity_list = UserActivity.objects.filter(user=user).exclude(activity__in=activity_list)
        context["activity_list"] = activity_list
        context["user_activity_list"] = user_activity_list
        context["user_activity_list"] = user_activity_list
        return context


class UserActivityDelete(DeleteView):
    model = UserActivity
    success_url = reverse_lazy('bee_django_referral:poster_list')

    # success_url = reverse_lazy('bee_django_crm:poster_list',kwargs={'pk': question_id})

    def get_success_url(self):
        user_activity = UserActivity.objects.get(pk=self.kwargs["pk"])
        user = user_activity.user
        return reverse_lazy('bee_django_referral:user_activity_list', kwargs={'user_id': user.id})

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


@method_decorator(cls_decorator(cls_name='UserActivityDetail'), name='dispatch')
class UserActivityDetail(DetailView):
    model = Activity
    template_name = 'bee_django_referral/custom_user/activity_detail.html'
    context_object_name = 'activity'

    def get_context_data(self, **kwargs):
        context = super(UserActivityDetail, self).get_context_data(**kwargs)
        user = self.request.user
        activity = Activity.objects.get(id=self.kwargs["pk"])
        _user_qrcode_list = UserShareImage().get_user_qrcode(user, activity.id)
        # print (_user_qrcode_list.first().qrcode)
        if not _user_qrcode_list.exists():
            UserShareImage().add_qrcode(activity, user)
        user_qrcode_list = UserShareImage().get_user_qrcode(user, activity.id)
        context["user_qrcode_list"] = user_qrcode_list
        return context

        # def get_context_data(self, **kwargs):
        #     context = super(UserActivityDetail, self).get_context_data(**kwargs)
        #     user = None
        #     activity_id=self.kwargs["activity_id"]
        #     user_qrcode_list = get_user_qrcode(user,activity_id=activity_id)
        #     return context


# =======User Activity =======

class PreuserRegRedirectView(RedirectView):
    query_string = False

    # 跳转到注册页，需接收qid参数
    def _get_url(self):
        return reverse('bee_django_crm:preuser_reg')

    def _get_invalid_url(self):
        return reverse('bee_django_referral:qrcode_invaild')

    def get_redirect_url(self, *args, **kwargs):
        # activity_id = self.kwargs["activity_id"]
        # user_id = self.request.GET["user_id"]
        qid = self.request.GET["qid"]
        qrcode, errcode = UserShareImage.check_qrcode_valid(qid)
        if errcode == 0:
            self.url = self._get_url() + "?qid=" + qrcode.id.__str__()
        else:
            self.url = self._get_invalid_url() + "?errcode=" + errcode.__str__()

        return super(PreuserRegRedirectView, self).get_redirect_url(*args, **kwargs)

    # template_name = 'bee_django_referral/reg/preuser_from.html'

    # 需接收referral_user_id1/source_id/t三个参数
    # 需接收user_id/activity_id/t三个参数
    # def _get_url(self):
    #     return reverse('bee_django_crm:preuser_reg')
    #
    # def get(self, request, *args, **kwargs):
    #
    #     t = self.request.GET["t"]
    #     user = User.objects.get(id=user_id)
    #     now = timezone.now()
    #     # error_message = None
    #     # qrcode = get_user_qrcode_image(user=user, activity_id=activity_id, timestamp=t)
    #     #
    #     # if qrcode:
    #     #     if not UserQrcodeStatus.user_qrcode_image_status_unused == qrcode.status:
    #     #         error_message = '此二维码已被使用过'
    #     #
    #     # try:
    #     #     activity = Activity.objects.get(id=activity_id)
    #     #     if now < activity.start_date:
    #     #         error_message = '活动未开始'
    #     #     elif activity.end_date < now:
    #     #         error_message = '活动已结束'
    #     # except:
    #     #     error_message = "发生错误"
    #
    #     return redirect(self._get_url() + "?user_id=" + user_id + "&t=" + t + "&activity_id=" + activity_id)

    # def get_context_data(self, **kwargs):
    #     context = super(PreuserReg, self).get_context_data(**kwargs)
    #     activity_id = self.kwargs["activity_id"]
    #     user_id = self.request.GET["user_id"]
    #     t = self.request.GET["t"]
    #     user = User.objects.get(id=user_id)
    #     now = timezone.now()
    #     error_message = None
    #
    #     context["error_message"] = error_message
    #     context["activity_id"] = activity_id
    #     return context
