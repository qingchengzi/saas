#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/6/19 22:42 
# ide： PyCharm
import collections
from django.shortcuts import render
from django.db.models import Count
from web import models


def dashboard(request, project_id):
    """概览"""
    # 问题数据处理
    # status_dict = {} # 字典在python3.6以后默认有序,如果是python3.6就直接这样写
    status_dict = collections.OrderedDict()  # python3.6之前使用
    for key, text in models.Issues.status_choices:
        status_dict[key] = {"text": text, "count": 0}
    issues_data = models.Issues.objects.filter(project_id=project_id).values("status").annotate(
        ct=Count("id"))  # 根据status进行分组，并对每一组计算数量并赋值给ct。annotate需要取的聚合条件,
    for item in issues_data:
        status_dict[item["status"]]["count"] = item["ct"]

    # 项目成员
    user_list = models.ProjectUser.objects.filter(project_id=project_id).values('user_id', 'user__username')
    # 最近的10个问题,条件是指派不为空（ssign__isnull=False）
    top_ten = models.Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by('-id')[0:10]
    context = {
        "status_dict": status_dict,
        "user_list": user_list,
        "top_ten_object": top_ten
    }
    return render(request, "dashboard.html", context)
