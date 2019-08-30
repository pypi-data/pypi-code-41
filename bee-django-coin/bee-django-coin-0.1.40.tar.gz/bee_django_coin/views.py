#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import random, datetime
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from .decorators import cls_decorator, func_decorator
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Count
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import CoinType, UserCoinRecord, UserCoinCount, OtherCoinCount, Item, Order
from .forms import CoinTypeForm, UserCoinRecordForm, OtherCoinCreateForm, ItemForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.utils import timezone

from .signals import send_message_signal
from .utils import get_user_name, get_default_name, get_coin_type
from .exports import get_user_coin, get_user_class_name, get_class_users, add_coin_record

User = get_user_model()


# Create your views here.
# =======course=======
def test(request):
    from exports import update_user_class_coin
    update_user_class_coin(1, 100)
    return


@method_decorator(cls_decorator(cls_name='CoinTypeList'), name='dispatch')
class CoinTypeList(ListView):
    template_name = 'bee_django_coin/coin_type/coin_type_list.html'
    context_object_name = 'coin_type_list'
    paginate_by = 20
    queryset = CoinType.objects.all()


# @method_decorator(cls_decorator(cls_name='MessageDetail'), name='dispatch')
# class CoinTypeDetail(DetailView):
#     model = Message
#     template_name = 'bee_django_message/message/message_detail.html'
#     context_object_name = 'message'


@method_decorator(permission_required('bee_django_coin.add_cointype'), name='dispatch')
class CoinTypeCreate(CreateView):
    model = CoinType
    form_class = CoinTypeForm
    template_name = 'bee_django_coin/coin_type/coin_type_form.html'


@method_decorator(permission_required('bee_django_coin.change_cointype'), name='dispatch')
class CoinTypeUpdate(UpdateView):
    model = CoinType
    form_class = CoinTypeForm
    template_name = 'bee_django_coin/coin_type/coin_type_form.html'


@method_decorator(permission_required('bee_django_coin.delete_cointype'), name='dispatch')
class CoinTypeDelete(DeleteView):
    model = CoinType
    success_url = reverse_lazy('bee_django_coin:coin_type_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


# 发金币记录
@method_decorator(cls_decorator(cls_name='UserRecordList'), name='dispatch')
class UserRecordList(ListView):
    template_name = 'bee_django_coin/record/user_record_list.html'
    context_object_name = 'record_list'
    paginate_by = 20
    queryset = None

    def get_user(self):
        user_id = self.kwargs["user_id"]
        try:
            user_table = get_user_model()
            user = user_table.objects.get(id=user_id)
        except:
            user = None
        return user

    def get_queryset(self):
        self.queryset = UserCoinRecord.objects.filter(user=self.get_user())
        return self.queryset

    def get_context_data(self, **kwargs):
        user = self.get_user()
        context = super(UserRecordList, self).get_context_data(**kwargs)
        context['user'] = user
        context['name'] = get_user_name(user)
        context['default_name'] = get_default_name
        context['sum_coin'] = get_user_coin(user)
        return context


# 发M币，增加一条记录
class UserRecordCreate(CreateView):
    model = UserCoinRecord
    form_class = UserCoinRecordForm
    template_name = 'bee_django_coin/record/form.html'

    def get_user(self):
        return get_object_or_404(get_user_model(), pk=self.kwargs["user_id"])

    def get_context_data(self, **kwargs):
        context = super(UserRecordCreate, self).get_context_data(**kwargs)
        user = self.get_user()
        context['name'] = get_user_name(user)
        return context

    def form_valid(self, form):
        if not self.request.user.has_perm('bee_django_coin.add_usercoinrecord'):
            messages.error(self.request, '没有权限')
            return super(UserRecordCreate, self).form_valid(form)
        user_record = form.save(commit=False)
        user = self.get_user()
        user_record.user = user
        user_record.created_by = self.request.user
        user_record.save()
        return super(UserRecordCreate, self).form_valid(form)


class UserRankList(ListView):
    template_name = 'bee_django_coin/rank/list.html'
    context_object_name = 'user_list'
    paginate_by = 100
    queryset = UserCoinCount.objects.all()

    def get_context_data(self, **kwargs):
        context = super(UserRankList, self).get_context_data(**kwargs)
        return context


class CustomUserRankList(UserRankList):
    template_name = 'bee_django_coin/rank/custom_list.html'


class OtherRecordList(ListView):
    model = UserCoinRecord
    template_name = 'bee_django_coin/other_coin/other_record_list.html'
    context_object_name = 'record_list'
    paginate_by = 20
    queryset = []

    def get_queryset(self):
        coin_identity = self.kwargs["coin_identity"]
        coin_content_id = self.kwargs["coin_content_id"]
        # 班级m币
        if coin_identity == 'user_class':
            self.queryset = UserCoinRecord.objects.filter(coin_type__identity=coin_identity,
                                                          coin_content_id=coin_content_id)
        return self.queryset

    def get_count(self):
        coin_identity = self.kwargs["coin_identity"]
        coin_content_id = self.kwargs["coin_content_id"]
        try:
            record = OtherCoinCount.objects.get(coin_type__identity=coin_identity, coin_content_id=coin_content_id)
            count = record.count
        except:
            count = 0
        return count

    def get_context_data(self, **kwargs):
        context = super(OtherRecordList, self).get_context_data(**kwargs)
        context['count'] = self.get_count()
        coin_identity = self.kwargs["coin_identity"]
        coin_content_id = self.kwargs["coin_content_id"]
        context['coin_content_id'] = coin_content_id
        if coin_identity == 'user_class':
            class_name = get_user_class_name(coin_content_id)
            context['title'] = "【" + class_name + "】"
        return context


class OtherRecordCreate(CreateView):
    model = UserCoinRecord
    form_class = None
    fields = ["coin", "user", "reason"]
    template_name = 'bee_django_coin/other_coin/form.html'

    # def get(self, request, *args, **kwargs):
    #     self.form_class=

    def get_success_url(self):
        return reverse('bee_django_coin:other_record_list', kwargs=self.kwargs)

    def get_count(self):
        coin_identity = self.kwargs["coin_identity"]
        coin_content_id = self.kwargs["coin_content_id"]
        try:
            record = OtherCoinCount.objects.get(coin_type__identity=coin_identity, coin_content_id=coin_content_id)
            count = record.count
        except:
            count = 0
        return count

    def get_context_data(self, **kwargs):
        coin_identity = self.kwargs["coin_identity"]
        coin_content_id = self.kwargs["coin_content_id"]
        context = super(OtherRecordCreate, self).get_context_data(**kwargs)
        context["count"] = self.get_count()
        # 班级剩余m币
        if coin_identity == "user_class":
            user_list = get_class_users(coin_content_id)
            context["form"] = OtherCoinCreateForm(user_list)
        return context

    @transaction.atomic
    def form_valid(self, form):
        if not self.request.user.has_perm("bee_django_coin.add_teach_class_coin"):
            messages.error(self.request, '没有权限')
            return redirect(reverse('bee_django_coin:other_record_add', kwargs=self.kwargs))
        count = self.get_count()
        if count < form.instance.coin:
            messages.error(self.request, '剩余数量不足')
            return redirect(reverse('bee_django_coin:other_record_add', kwargs=self.kwargs))
        coin_identity = self.kwargs["coin_identity"]
        coin_content_id = self.kwargs["coin_content_id"]
        coin_type = get_coin_type(coin_identity)
        form.instance.coin_type = coin_type
        form.instance.coin_content_id = coin_content_id
        form.instance.created_by = self.request.user
        return super(OtherRecordCreate, self).form_valid(form)


# =======商城===========
# ==商品==
class ItemList(ListView):
    template_name = 'bee_django_coin/shop/item/list.html'
    context_object_name = 'item_list'
    paginate_by = 20
    queryset = Item.objects.all()


class ItemDetail(DetailView):
    model = Item
    template_name = 'bee_django_coin/shop/item/detail.html'
    context_object_name = 'item'


@method_decorator(cls_decorator(cls_name='CourseCreate'), name='dispatch')
class ItemCreate(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'bee_django_coin/shop/item/form.html'


class ItemUpdate(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'bee_django_coin/shop/item/form.html'


class ItemDelete(DeleteView):
    model = Item
    success_url = reverse_lazy('bee_django_coin:item_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


# 用户的商城商品列表页
class ItemCustomList(ItemList):
    template_name = 'bee_django_coin/shop/item/custom_list.html'
    queryset = Item.objects.filter(status=1)  # 只显示上架的


class ItemCustomDetail(ItemDetail):
    template_name = 'bee_django_coin/shop/item/custom_detail.html'


# =====订单====

class OrderList(ListView):
    template_name = 'bee_django_coin/shop/order/list.html'
    context_object_name = 'order_list'
    paginate_by = 20
    queryset = Order.objects.all()


class OrderDetail(DetailView):
    model = Order
    template_name = 'bee_django_coin/shop/order/detail.html'
    context_object_name = 'order'
    queryset = Order.objects.all()


class OrderCreate(TemplateView):
    def post(self, request, *args, **kwargs):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        user_id = request.POST.get("user_id")
        item_id = request.POST.get("item_id")
        item_count = request.POST.get("item_count")
        total_coin = request.POST.get("total_coin")

        try:
            item = Item.objects.get(id=item_id)
        except:
            return JsonResponse(data={
                'error': 1,
                'message': '商品错误'
            })
        try:
            user = User.objects.get(id=user_id)
        except:
            return JsonResponse(data={
                'error': 1,
                'message': '用户错误'
            })
        if user.userprofile.is_pause == True:
            return JsonResponse(data={
                'error': 1,
                'message': '到期用户无法购买商品'
            })
        total_coin = int(total_coin)
        user_coin_count = get_user_coin(user)
        if user_coin_count < total_coin:
            return JsonResponse(data={
                'error': 1,
                'message': settings.COIN_NAME.decode("utf-8") + u'数量不足'
            })
        order = Order()
        order.user = user
        now = timezone.now()
        r = random.randint(0, 999)
        order.order_id = now.strftime("%Y%m%d%H%M%S") + str(r).zfill(3) + user.id.__str__()
        order.item_id = item_id
        order.item_name = item.name
        order.item_count = item_count
        order.item_coin = total_coin
        order.save()
        order.change_status_info(self.request.user, 1)
        reason = '购买' + item_count.__str__() + '份商品:' + item.name
        coin = add_coin_record(to_user=user, reason=reason, identity='coin_item', coin=-total_coin, count=1,
                               created_by=None)
        if coin:
            error, msg = order.change_status_info(self.request.user, 2)
            return JsonResponse(data={
                'error': error,
                'message': msg
            })
        else:
            return JsonResponse(data={
                'error': 1,
                'message': '支付失败'
            })


class OrderUpdateStatus(TemplateView):
    def post(self, request, *args, **kwargs):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        order_id = request.POST.get("order_id")
        status = request.POST.get("status")

        try:
            order = Order.objects.get(id=order_id)
        except:
            return JsonResponse(data={
                'error': 1,
                'message': '订单错误'
            })
        error, msg = order.change_status_info(request.user, status)
        return JsonResponse(data={
            'error': error,
            'message': msg
        })


class OrderUserList(ListView):
    template_name = 'bee_django_coin/shop/order/user_list.html'
    context_object_name = 'order_list'
    paginate_by = 20
    queryset = None

    def get_user(self):
        return User.objects.get(id=self.kwargs["user_id"])

    def get_context_data(self, **kwargs):
        user = self.get_user()
        context = super(OrderUserList, self).get_context_data(**kwargs)
        context['user'] = user
        return context

    def get_queryset(self):
        user = self.get_user()
        return Order.objects.filter(user=user)


class OrderCustomUserList(OrderUserList):
    template_name = 'bee_django_coin/shop/order/custom_user_list.html'


class OrderCustomUserDetail(OrderDetail):
    template_name = 'bee_django_coin/shop/order/custom_user_detail.html'
