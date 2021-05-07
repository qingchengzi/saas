#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/5 21:29 
# ide： PyCharm
from django.shortcuts import render

from web.forms.project import ProjectModeForm
from django.http import JsonResponse


def project_list(request):
    """
    项目列表
    :param request:
    :return:
    """
    if request.method == "GET":
        form = ProjectModeForm(request)
        return render(request, "project_list.html", {"form": form})
    form = ProjectModeForm(request, data=request.POST)
    if form.is_valid():
        # 验证通过:用户提交了项目名、颜色、描述，还需要谁创建的项目
        form.instance.creator = request.tracer.user  # 当前用户创建的项目
        # 创建项目
        form.save()
        return JsonResponse({"status": True})

    return JsonResponse({"status": False, "error": form.errors})
