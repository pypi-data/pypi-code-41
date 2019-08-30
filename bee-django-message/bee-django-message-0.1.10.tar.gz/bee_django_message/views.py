#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import json
from django.utils import timezone
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from .decorators import cls_decorator, func_decorator
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Count
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Message, SendRecord
from .forms import MessageForm, RecordChangeDoneForm, RecordSearchForm
from .utils import get_user_name, JSONResponse
from .exports import send_message
from .signals import send_message_signal

User = get_user_model()


# Create your views here.
# =======course=======
def test(request):
    from exports import send_message
    from django.contrib.auth.models import User
    user = User.objects.all().first()
    res = send_message(to_user=None, from_user=user, message_identity='course_alert', title='test', url=None)
    print(res)
    return HttpResponse('OK')


@method_decorator(cls_decorator(cls_name='MessageList'), name='dispatch')
class MessageList(ListView):
    template_name = 'bee_django_message/message/message_list.html'
    context_object_name = 'message_list'
    paginate_by = 20
    queryset = Message.objects.all()


@method_decorator(cls_decorator(cls_name='MessageDetail'), name='dispatch')
class MessageDetail(DetailView):
    model = Message
    template_name = 'bee_django_message/message/message_detail.html'
    context_object_name = 'message'


@method_decorator(cls_decorator(cls_name='MessageCreate'), name='dispatch')
class MessageCreate(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'bee_django_message/message/message_form.html'


@method_decorator(cls_decorator(cls_name='MessageUpdate'), name='dispatch')
class MessageUpdate(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'bee_django_message/message/message_form.html'


@method_decorator(cls_decorator(cls_name='MessageDelete'), name='dispatch')
class MessageDelete(DeleteView):
    model = Message
    success_url = reverse_lazy('bee_django_message:message_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


# 后台显示消息记录
class RecordList(ListView):
    template_name = 'bee_django_message/record/message_record_list.html'
    context_object_name = 'record_list'
    paginate_by = 20
    queryset = None

    def get_message(self):
        message_id = self.kwargs["message_id"]
        message = Message.objects.get(id=message_id)
        return message

    def search(self):
        is_done = self.request.GET.get("is_done")
        message = self.get_message()
        self.queryset = SendRecord.objects.filter(message=message)

        is_done_value = None
        if not is_done in ["0", 0, None, ""]:
            if is_done in [1, "1"]:
                is_done_value = True
            elif is_done in [-1, "-1"]:
                is_done_value = False
            self.queryset = self.queryset.filter(is_done=is_done_value)

        return self.queryset

    def get_queryset(self):
        return self.search()

    def get_context_data(self, **kwargs):
        context = super(RecordList, self).get_context_data(**kwargs)
        message = self.get_message()
        is_done = self.request.GET.get("is_done")
        context['message'] = message
        context['search_form'] = RecordSearchForm({"is_done": is_done})
        return context


class RecordDetail(DetailView):
    model = SendRecord
    template_name = 'bee_django_message/record/record_detail.html'
    context_object_name = 'record'

class RecordCustomDetail(RecordDetail):
    template_name = 'bee_django_message/record/record_custom_detail.html'

# 修改后台显示的消息
class RecordUpdate(UpdateView):
    model = SendRecord
    form_class = RecordChangeDoneForm
    template_name = 'bee_django_message/record/record_change_done.html'

    def get_success_url(self):
        return reverse_lazy('bee_django_message:record_detail', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        record = SendRecord.objects.get(id=self.kwargs["pk"])
        context = super(RecordUpdate, self).get_context_data(**kwargs)
        context['record'] = record
        return context

    def form_valid(self, form):
        record = form.instance
        record.is_done = True
        record.done_at = timezone.now()
        record.done_by = self.request.user
        if record.message.need_reply:
            send_message(to_user=record.from_user,title=record.get_reply_title(),info=record.get_reply_info(),url=record.get_reply_url())
        return super(RecordUpdate, self).form_valid(form)


# 发送记录
@method_decorator(cls_decorator(cls_name='UserRecordList'), name='dispatch')
class CustomUserRecordList(ListView):
    template_name = 'bee_django_message/record/custom_user_record_list.html'
    context_object_name = 'record_list'
    paginate_by = 20
    queryset = None

    def get_user(self):
        user_id = self.kwargs["user_id"]
        if user_id in [None, "0"]:
            return None
        user = User.objects.get(id=user_id)
        return user

    def get_queryset(self):
        user = self.get_user()
        self.queryset = SendRecord.objects.filter(to_user=user)
        return self.queryset

    def get_context_data(self, **kwargs):
        user = self.get_user()
        context = super(CustomUserRecordList, self).get_context_data(**kwargs)
        context['user'] = user
        return context


#
# @method_decorator(cls_decorator(cls_name='RecordDetail'), name='dispatch')
# class RecordDetail(DetailView):
#     model = SendRecord
#     template_name = 'bee_django_message/message/message_detail.html'
#     context_object_name = 'record'


@method_decorator(cls_decorator(cls_name='UserRecordClick'), name='dispatch')
class UserRecordClick(TemplateView):
    def post(self, request, *args, **kwargs):
        record_id = request.POST.get("record_id")
        record = SendRecord.objects.get(id=record_id)
        record.is_view = True
        record.save()
        return JSONResponse(json.dumps({"url": record.url}, ensure_ascii=False))


class UserRecordAllClick(TemplateView):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            pass
        except:
            res = {"error": 1, "message": "参数错误"}
            return JSONResponse(json.dumps(res, ensure_ascii=False))
        record_list = SendRecord.objects.filter(to_user=user, is_view=False)
        for record in record_list:
            record.is_view = True
            record.save()
        res = {"error": 0, "message": "操作成功"}
        return JSONResponse(json.dumps(res, ensure_ascii=False))

