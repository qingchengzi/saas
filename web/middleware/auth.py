#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/4 22:42 
# ide： PyCharm

import datetime

from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from web import models


class Tracer:

    def __init__(self):
        self.user = None
        self.price_policy = None


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """
        如果用户已登录，在request中赋值
        :param request:
        :return:
        """
        request.tracer = Tracer()
        # 用户已登录就会有user_id,如果没有给0
        user_id = request.session.get("user_id", 0)
        # 如果user_object对象有值说明已经登录
        user_object = models.UserInfo.objects.filter(id=user_id).first()
        request.tracer.user = user_object
        # 白名单:没有登录都可以访问的url
        """
        1、获取当前用户访问的URL
        2、检查URL是否在白名单中，如果再则可以继续访问，相反判断是否已经登录
        """
        # 获取当前访问的url，然后判断是否在白名单中
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return
        # 检测用户是否已登录，如果已登录继续往后走，未登录则返回到登录页面
        if not request.tracer.user:
            return redirect("login")
        # 登录成功之后，访问后台管理时：获取当前用户所拥有的额度
        # 方式一：免费额度在交易记录中存储
        # 获取当前用户ID值最大（最近的交易记录)的交易记录，状态是已支付。场景就是：开始免费版(id最小是免费版)，然后升级了，然后又升级了，这个时候我们获取最后一次的交易记录。
        _object = models.Transaction.objects.filter(user=user_object, status=2).order_by("-id").first()
        # 判断是否已过期
        current_datetime = datetime.datetime.now()
        # _object.end_datetime 为空是免费版，所以这里要判断。判断是否已过期
        if _object.end_datetime and _object.end_datetime < current_datetime:
            _object = models.Transaction.objects.filter(user=user_object, status=2, price_policy__category=1).first()
        # 当前登录用户的额度信息
        request.tracer.price_policy = _object.price_policy
        """
        # 方式二：免费的额度存储在配置文件
        _object = models.Transaction.objects.filter(user=user_object, status=2).order_by("-id").first()
        # 没有购买就是免费版
        if not _object:
            # 没有购买
            request.price_policy = models.PricePolicy.objects.filter(category=1, title="个人免费版").first()
        else:
            # 付费版,先判断有没有过期
            current_datetime = datetime.datetime.now()
            if _object.end_datetime and _object.end_datetime < current_datetime:
                # 过期后价格策略享受免费版
                request.price_policy = models.PricePolicy.objects.filter(category=1, title="个人免费版").first()
            else:
                request.price_policy = _object.price_policy
        """
