#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/4/30 14:13 
# ide： PyCharm

"""
用户账号相关的功能：注册、短信、登录、注销
"""

from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from web.forms.account import RegisterModelForm, SendSmsForm

from web import models
from django.conf import settings


def register(request):
    """注册"""
    if request.method == "GET":
        form = RegisterModelForm()
        return render(request, 'register.html', {'form': form})
    form = RegisterModelForm(data=request.POST)
    if form.is_valid():
        # 验证通过，写入数据库(数据库密码要是密文)
        form.save()
        # instance=form.save()相当于instance=models.UserInfo.objects.create(**form.cleaned_data)
        # 通过form.save()来保存，会自动把数据库中没有的字段去除，create会将所有的字段都提交到数据库，会报错。
        return JsonResponse({'status': True, 'data': '/login/'})
    return JsonResponse({'status': False, 'error': form.errors})


def send_sms(request):
    """发送短信"""
    print(request.GET)
    form = SendSmsForm(request, data=request.GET)
    # 只是校验手机号：不能为空、格式是否正确
    if form.is_valid():
        # 发短信
        # 写redis
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})  # 主要有错误信息都会放到form.errors中
