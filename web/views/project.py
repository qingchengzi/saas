#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/5 21:29 
# ide： PyCharm
from django.shortcuts import render


def project_list(request):
    """
    项目列表
    :param request:
    :return:
    """
    # 获取当前登录用户的信息
    print(request.tracer.user)
    # 获取当前价格策略信息
    print(request.tracer.price_policy)

    return render(request, "project_list.html")
