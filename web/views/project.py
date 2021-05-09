#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/5 21:29 
# ide： PyCharm
from django.shortcuts import render, HttpResponse, redirect

from web.forms.project import ProjectModeForm
from django.http import JsonResponse

from web import models


def project_list(request):
    """
    项目列表
    :param request:
    :return:
    """
    if request.method == "GET":
        # GET请求查看项目列表
        """
        1、从数据库中获取两部分数据：
            我创建的所有项目：已星标、未星标
            我参与的所有项目：已星标、未星标
            
        2、提取已星标
            列表 = 循环【我创建的所有项目】 + [我参与的所有项目] 把已星标的数据提取处理
            得到三个列表：星标、创建、参与
        """
        # 区分：用户创建项目 和 用户参与项目
        # 存放创建项目和参与项目的对象，(当前用户创建项目、当前用户参与者的星标对象放到star，(当前用户创建项目）无星标对象放到my,join无星标存放项目参与者
        project_dict = {"star": [], "my": [], "join": []}
        # 查询当前用户创建的所有项目
        my_project_list = models.Project.objects.filter(creator=request.tracer.user)
        for row in my_project_list:
            if row.star:  # 星标为true放到star
                project_dict['star'].append({"value": row, "type": "my"})
            else:
                project_dict['my'].append(row)

        # 当前用户参与的所有项目
        join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.start:
                project_dict['star'].append({"values": item.project,
                                             "type": "join"})  # project_dict字典中star已添加了项目的对象，这里在添加对象以后取值就会混乱,所有添加项目参与者项目
            else:
                project_dict['join'].append(item.project)  # 用户参与项目无星标放到join中

        form = ProjectModeForm(request)
        return render(request, "project_list.html", {"form": form, "project_dict": project_dict})
    # POST,对话框的ajax添加项目
    form = ProjectModeForm(request, data=request.POST)
    if form.is_valid():
        # 验证通过:用户提交了项目名、颜色、描述，还需要谁创建的项目
        form.instance.creator = request.tracer.user  # 当前用户创建的项目
        # 创建项目
        form.save()
        return JsonResponse({"status": True})

    return JsonResponse({"status": False, "error": form.errors})


def project_star(request, project_type, project_id):
    """项目添加星标,需要区分我创建的项目和我参与的项目"""
    if project_type == "my":
        models.Project.objects.filter(id=project_id, creator=request.tracer.user).update(
            star=True)  # 我选的项目必须是我创建的通过creator参数赋值为当前用户来限制，目的是为了防止别人在url中直接修改id后改变项目状态
        return redirect("project_list")
    if project_type == "join":  # 我参与的项目
        models.Project.objects.filter(project_id=project_id, user=request.tracer.user).update(star=True)
        return redirect("project_list")
    return HttpResponse("请求错误")


def project_unstar(request, project_type, project_id):
    """
    取消星标，需要判断是我创建的项目，还是我参与的项目
    通过显示项目列表时project_list函数中project_dict字典中type值进行判断
    :param request:
    :param project_type:
    :param project_id:
    :return:
    """
    if project_type == "my":
        models.Project.objects.filter(id=project_id, creator=request.tracer.user).update(
            star=False)
        return redirect("project_list")
    if project_type == "join":
        models.Project.objects.filter(project_id=project_id, user=request.tracer.user).update(star=False)
        return redirect("project_list")
    return HttpResponse("请求错误")
