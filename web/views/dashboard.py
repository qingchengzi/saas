#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/6/19 22:42 
# ide： PyCharm
import time
import datetime
import collections
from django.shortcuts import render
from django.http import JsonResponse
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


def issues_chart(request, project_id):
    """
    在概览页面生成highcharts所需的数据
    :param request:
    :param project_id:
    :return:
    """
    today = datetime.datetime.now().date()  # 只获取年月日,不要时分秒
    data_dict = collections.OrderedDict()  # 创建有序字典
    for i in range(0, 30):
        date = today - datetime.timedelta(days=i)  # 每一天的时间
        data_dict[date.strftime("%Y-%m-%d")] = [time.mktime(date.timetuple()) * 1000, 0]

    # 最近30天，每天创建的问题的数量.
    # 去数据库中查询最近30天的所有数据 & 根据日期每天分组
    # select xxxx,1 as ctime from xxxx
    # select id,name,email from table;
    # select id,name, strftime("%Y-%m-%d",create_datetime) as ctime from table;
    # mysql字符串格式化："DATE_FORMAT(web_transaction.create_datetime,'%%Y-%%m-%%d')"
    # sqllite的strftime('%%Y-%%m-%%d',web_issues.create_datetime)
    result = models.Issues.objects.filter(project_id=project_id,
                                          create_datetime__gte=today - datetime.timedelta(days=30)).extra(
        select={'ctime': "strftime('%%Y-%%m-%%d',web_issues.create_datetime)"}).values('ctime').annotate(ct=Count('id'))
    # print(result)
    # <QuerySet [{'ctime': '2021-06-11', 'ct': 2}, {'ctime': '2021-06-12', 'ct': 1}]>
    for item in result:
        data_dict[item['ctime']][1] = item['ct']

    return JsonResponse({"status": True, "data": list(data_dict.values())})
