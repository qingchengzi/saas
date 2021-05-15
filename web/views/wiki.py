#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/11 21:49 
# ide： PyCharm

from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.http import JsonResponse
from web.forms.wiki import WkiModelForm
from web import models


def wiki(request, project_id):
    """
    wiki的首页展示
    :param request:
    :param project_id:
    :return:
    """
    wiki_id = request.GET.get("wiki_id")
    if not wiki_id or not wiki_id.isdecimal():  # 不存在或者不是十进制的小数
        return render(request, "wiki.html")
    wiki_object = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    return render(request, "wiki.html", {"wiki_object": wiki_object})


def wiki_add(request, project_id):
    """
    wiki添加
    :param request:
    :param project_id:
    :return:
    """
    if request.method == "GET":
        form = WkiModelForm(request)
        return render(request, "wiki_add.html", {"form": form})
    form = WkiModelForm(request, data=request.POST)
    if form.is_valid():
        # 判断用户是否已经选择父文章
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.instance.project = request.tracer.project
        form.save()
        url = reverse('wiki', kwargs={"project_id": project_id})
        return redirect(url)
    return render(request, "wiki_add.html", {"form": form})


def wiki_catalog(request, project_id):
    """
    wiki目录
    :param request:
    :return:
    """
    # 获取当前项目所有的目录
    data = models.Wiki.objects.filter(project=request.tracer.project).values("id", "title", "parent_id").order_by(
        'depth', 'id')
    # data是querySet类型,需要转换为list类型
    return JsonResponse({"status": True, "data": list(data)})
