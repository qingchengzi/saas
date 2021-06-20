#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/9 16:53 
# ide： PyCharm
from django.template import Library
from web import models
from django.urls import reverse  # url进行反向解析用

register = Library()


@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
    # 1、获取我创建的所有项目,creator=当前登录的用户
    my_project_list = models.Project.objects.filter(creator=request.tracer.user)
    # 2、获取我参与的所有项目
    join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
    return {"my": my_project_list, "join": join_project_list, "request": request}


@register.inclusion_tag('inclusion/manage_menu_list.html')
def manage_menu_list(request):
    """
    导航菜单选中状态
    :param request:
    :return:
    """
    data_list = [
        {"title": "概览", "url": reverse("dashboard", kwargs={"project_id": request.tracer.project.id})},
        {"title": "问题", "url": reverse("issues", kwargs={"project_id": request.tracer.project.id})},
        {"title": "统计", "url": reverse("statistics", kwargs={"project_id": request.tracer.project.id})},
        {"title": "wiki", "url": reverse("wiki", kwargs={"project_id": request.tracer.project.id})},
        {"title": "文件", "url": reverse("file", kwargs={"project_id": request.tracer.project.id})},
        {"title": "配置", "url": reverse("setting", kwargs={"project_id": request.tracer.project.id})},
    ]
    for item in data_list:
        # 循环的url和当前用户访问的url:request.path_info: /manage/4/issues/xxx/add/进行比较
        if request.path_info.startswith(item['url']):
            item['class'] = "active"
    return {"data_list": data_list}
