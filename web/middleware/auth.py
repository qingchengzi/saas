#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/4 22:42 
# ide： PyCharm

from django.utils.deprecation import MiddlewareMixin
from web import models


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """
        如果用户已登录，在request中赋值
        :param request:
        :return:
        """
        # 用户已登录就会有user_id,如果没有给0
        user_id = request.session.get("user_id", 0)
        # 如果user_object对象有值说明已经登录
        user_object = models.UserInfo.objects.filter(id=user_id).first()
        request.trace = user_object
