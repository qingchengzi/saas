#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/4/30 14:13 
# ide： PyCharm

"""
用户账号相关的功能：注册、短信、登录、注销
"""
import uuid
import datetime

from django.shortcuts import render, HttpResponse, redirect
from django.db.models import Q
from django.http import JsonResponse
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSMSForm, LoginForm

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
        # 通过form.save()来保存，会自动把数据库中没有的字段去除，create会将所有的字段都提交到数据库，会报错。
        # form.save()  # 用户表新建一条数据(注册)
        instance = form.save()  # 相当于instance=models.UserInfo.objects.create(**form.cleaned_data)
        # 创建交易记录
        # 方式1:免费额度存储在交易记录中
        # 对应中间件auth.py 方式1
        policy_object = models.PricePolicy.objects.filter(category=1, title="个人免费版").first()
        models.Transaction.objects.create(
            status=2,
            order=str(uuid.uuid4()),
            user=instance,
            price_policy=policy_object,
            count=0,
            price=0,
            start_datetime=datetime.datetime.now(),
        )

        # 方式二 对应auth.py 方式2 ，方式2在这里什么都不写，把方式1全部注释即可.

        return JsonResponse({'status': True, 'data': '/login/'})
    return JsonResponse({'status': False, 'error': form.errors})


def login_sms(request):
    """
    短信登录
    :param request:
    :return:
    """
    if request.method == "GET":
        form = LoginSMSForm()
        return render(request, "login_sms.html", {"form": form})
    form = LoginSMSForm(request.POST)
    if form.is_valid():
        # 用户输入正确，登录成功
        user_object = form.cleaned_data['mobile_phone']
        # 用户信息放入session
        request.session["user_id"] = user_object.id
        # request.session["user_name"] = user_object.username
        request.session.set_expiry(60 * 60 * 24 * 14)
        return JsonResponse({"status": True, "data": "/index/"})
    return JsonResponse({"status": False, "error": form.errors})


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


def login(request):
    """
    输入用户名和密码登录
    :return:
    """
    if request.method == "GET":
        form = LoginForm(request)
        return render(request, "login.html", {"form": form})
    form = LoginForm(request, data=request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        # 用户名和密码的登录
        # user_object = models.UserInfo.objects.filter(username=username, password=password).first()
        # (手机=username and pwd=pwd) or (邮箱=username and pwd=pwd)
        user_object = models.UserInfo.objects.filter(Q(email=username) | Q(mobile_phone=username)).filter(
            password=password).first()
        if user_object:
            # 用户名密码正确,登录成功
            request.session["user_id"] = user_object.id
            request.session.set_expiry(60 * 60 * 24 * 14)  # 2周
            return redirect('index')
        form.add_error('username', '用户名或密码错误')
    return render(request, "login.html", {"form": form})


def image_code(request):
    """生成图片验证码"""
    from io import BytesIO
    from utils.image_code import check_code
    image_object, code = check_code()
    #  图片验证码保存到session中
    request.session['image_code'] = code
    # 定义session的过期时间，默认是两周，这里自定义60秒过期
    request.session.set_expiry(60)
    stream = BytesIO()
    image_object.save(stream, "png")
    return HttpResponse(stream.getvalue())


def logout(request):
    """退出"""
    # 清空session中的值
    request.session.flush()
    return redirect("index")
