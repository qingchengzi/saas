#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/11 21:49 
# ide： PyCharm

from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # 去除csrf验证装饰器

from web.forms.wiki import WkiModelForm
from web import models

from utils.encrypt import uid
from utils.tencent.cos import upload_file


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
        return render(request, "wiki_form.html", {"form": form})
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
    return render(request, "wiki_form.html", {"form": form})


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


def wiki_delete(request, project_id, wiki_id):
    """
    删除文章
    :param request:
    :param project_id:
    :return:
    """
    # 必须传project_id,要不然直接修改url上的ID，就会导致删除别人的文章
    models.Wiki.objects.filter(project_id=project_id, id=wiki_id).delete()
    # 删除完成后返回到用户列表页面
    url = reverse('wiki', kwargs={"project_id": project_id})
    return redirect(url)


def wiki_edit(request, project_id, wiki_id):
    """
    编辑文章
    :param request:
    :param project_id:
    :param wiki_id:
    :return:
    """
    wiki_object = models.Wiki.objects.filter(project_id=project_id, id=wiki_id).first()
    if not wiki_object:
        url = reverse('wiki', kwargs={"project_id": project_id})
        return redirect(url)
    if request.method == "GET":
        form = WkiModelForm(request, instance=wiki_object)
        return render(request, "wiki_form.html", {"form": form})
    form = WkiModelForm(request, data=request.POST, instance=wiki_object)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.save()
        url = reverse('wiki', kwargs={"project_id": project_id})
        preview_url = "{0}?wiki_id={1}".format(url, wiki_id)
        return redirect(preview_url)
    return render(request, "wiki_form.html", {"form": form})


@csrf_exempt
def wiki_upload(request, project_id):
    """markdown插件上传图片"""
    result = {
        "success": 0,
        "message": None,
        "url": None
    }
    # 用户上传的图片对象
    image_object = request.FILES.get("editormd-image-file")
    if not image_object:
        result["message"] = "文件不存在"
        return JsonResponse(result)
    # 上传到cos中的文件名不能重复,如果重复最新的会覆盖就文件，所有这里需要生成唯一数的文件名
    ext = image_object.name.rsplit(".")[-1]  # 获取上传文件后缀名
    key = "{0}.{1}".format(uid(request.tracer.user.mobile_phone), ext)
    image_url = upload_file(
        bucket=request.tracer.project.bucket,  # 文件对象上传到当前项目的桶中
        region=request.tracer.project.region,
        file_object=image_object,
        key=key
    )
    result["success"] = 1
    result["url"] = image_url
    return JsonResponse(result)
