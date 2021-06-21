#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/6/20 22:00 
# ide： PyCharm

from django.shortcuts import render


def statistics(request, project_id):
    """
    统计页面
    :param request:
    :param project_id:
    :return:
    """
    return render(request, "statistics.html")
