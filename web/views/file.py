#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/24 20:04
# ide： PyCharm

import json
import requests

from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms import model_to_dict  # 文件夹列表头部面包屑导航
from django.urls import reverse
from web.forms.file import FolderModelForm, FileModelForm
from web import models

from utils.tencent.cos import delete_file, delete_file_list, credential


# http://127.0.0.1:8000/manage/1/file/ 这样的url添加的时候是根目录
# http://127.0.0.1:8000/manage/1/file/?folder=9 这样的url获取参数folder，不是根目录
def file(request, project_id):
    """文件夹列表&添加文件夹"""
    parent_object = None
    folder_id = request.GET.get("folder", "")
    if folder_id.isdecimal():
        parent_object = models.FileRepository.objects.filter(id=int(folder_id), file_type=2,
                                                             project=request.tracer.project).first()
    # GET查看页面
    if request.method == "GET":
        # 面包屑导航条
        breadcrumb_list = []
        parent = parent_object
        while parent:
            # 方法1： breadcrumb_list.insert(0, {"id": parent.id, "name": parent.name})
            breadcrumb_list.insert(0, model_to_dict(parent, ['id', 'name']))  # 自动去parent对象中取id和name,然后拼凑为字典,和方法1效果上一样
            parent = parent.parent

        # 当前目录下所有的文件 & 文件夹获取到即可
        queryset = models.FileRepository.objects.filter(project=request.tracer.project)
        if parent_object:
            # 进入某目录
            file_object_list = queryset.filter(parent=parent_object).order_by("-file_type")
        else:
            # 根目录,没有父级目录
            file_object_list = queryset.filter(parent__isnull=True).order_by("-file_type")
        form = FolderModelForm(request, parent_object)
        context = {
            "form": form,
            "file_object_list": file_object_list,
            "breadcrumb_list": breadcrumb_list,
            "folder_obj": parent_object  # 当前目录
        }
        return render(request, "file.html", context)

    # POST添加文件夹 & 文件夹的修改
    fid = request.POST.get("fid", "")  # fid为空说明是添加,有值说明是编辑
    edit_object = None
    if fid.isdecimal():  # 修改
        edit_object = models.FileRepository.objects.filter(id=int(fid), file_type=2,
                                                           project=request.tracer.project).first()
    if edit_object:  # 编辑
        form = FolderModelForm(request, parent_object, data=request.POST, instance=edit_object)
    else:  # 添加
        form = FolderModelForm(request, parent_object, data=request.POST)

    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_object
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


# 用户发来删除url格式:http://127.0.0.1:8000/manage/1/file/delete/?fid=1
def file_delete(request, project_id):
    """
      删除文件(数据库中文件删除，cos文件删除,当前项目已使用的空间容量还原
      删除文件夹(找到该文件夹下所有的文件都要进行-->数据库中和cos删除,当前项目已使用的空间容量还原
    :param request:
    :param project:
    :return:
    """
    fid = request.GET.get("fid")
    # 删除数据库中的文件 & 文件夹 (级联删除)
    delete_object = models.FileRepository.objects.filter(id=fid, project=request.tracer.project).first()
    if delete_object.file_type == 1:
        # 删除文件(数据库中文件删除，cos文件删除,当前项目已使用的空间容量还原
        # 删除文件时，将容量还给当前项目。先找到当前项目已使用空间,然后减去当前文件大小
        request.tracer.project.user_space -= delete_object.file_size  # 单位是字节
        request.tracer.project.save()
        # cos中删除文件
        delete_file(request.tracer.project.bucket, request.tracer.project.region, delete_object.key)
        # 在数据库中删除
        delete_object.delete()
        return JsonResponse({'status': True})

    # 删除文件夹(找到该文件夹下所有的文件都要进行-->数据库中和cos删除,当前项目已使用的空间容量还原
    total_size = 0
    key_list = []  # 文件所有的key

    folder_list = [delete_object, ]  # 目录列表
    for folder in folder_list:  # 文件夹下面的所有文件和文件夹
        child_list = models.FileRepository.objects.filter(project=request.tracer.project, parent=folder).order_by(
            "-file_type")
        for child in child_list:
            if child.file_type == 2:  # 文件夹,添加到folder_list中
                folder_list.append(child)
            else:  # 文件大小汇总
                total_size += child.file_size
                # 删除文件,每次都删除一个文件,效率低
                # delete_file(request.tracer.project.bucket, request.tracer.project.region, child.key)
                # 腾讯提供的批量删除
                key_list.append({"Key": child.key})
    # cos批量删除文件
    if key_list:
        delete_file_list(request.tracer.project.bucket, request.tracer.project.region, key_list)
    # 归还容量
    if total_size:
        request.tracer.project.user_space -= total_size
        request.tracer.project.save()
    # 删除数据库中的文件
    delete_object.delete()
    return JsonResponse({"status": True})


@csrf_exempt
def cos_credential(request, project_id):
    """
    获取cos上传临时凭证
    # 做容量限制：单文件 & 总容量
    :param request:
    :return:
    """
    # 单文件限制的大小,数据库中单位M，将M转换为字节，因为前端传过来是字节
    per_file_limit = request.tracer.price_policy.per_file_size * 1024 * 1024
    total_file_limit = request.tracer.price_policy.project_space * 1024 * 1024 * 1024
    total_size = 0
    file_list = json.loads(request.body.decode("utf-8"))
    for item in file_list:
        # 上传文件的字节大小，单位字节 item['size'] = B
        if item.get('size') > per_file_limit:  # 单文件超出限制
            msg = "单文件超出限制(最大{0}M，文件:{1},请升级套餐。".format(request.tracer.price_policy.per_file_size, item["name"])
            return JsonResponse({"status": False, "error": msg})
        total_size += item['size']

    # 总容量进行限制
    # request.tracer.price_policy.project_space  # 项目的允许的空间
    # request.tracer.project.user_space  # 项目已使用的空间
    if request.tracer.project.user_space + total_size > total_file_limit:
        return JsonResponse({"status": False, "error": "容量超过限制，请升级套餐"})

    data_dict = credential(request.tracer.project.bucket, request.tracer.project.region)
    return JsonResponse({"status": True, "data": data_dict})


@csrf_exempt
def file_post(request, project_id):
    """
    已上传成功的文件写入到数据库
    前端传来的值：
        name:fileName,
        key:key,
        file_size:fileSize,
        parent:CURRENT_FOLDER_ID,// 当前访问的目录id
        etag:data.ETag, // 腾讯对象返回的id
        file_path:data.Location
    :param request:
    :param project_id:
    :return:
    """
    # 根据key再去cos获取文件Etag和
    # 把获取到的数据写入到数据库
    form = FileModelForm(request, data=request.POST)
    if form.is_valid():
        # 校验通过:数据写入到数据库
        # 通过ModelForm.save存储到数据库中的数据返回的instance对象，无法通过get_xx_display获取choice的中文
        # form.instance.file_type = 1
        # form.update_user = request.tracer.user
        # instance = form.save()
        # 使用第二种方法，能通过get_xx_display获取choice的中文
        data_dict = form.cleaned_data  # 验证成功后的字段
        data_dict.pop("etag")  # models模型中没有etag字段，所以去除
        data_dict.update({"project": request.tracer.project, "file_type": 1, "update_user": request.tracer.user})
        instance = models.FileRepository.objects.create(**data_dict)

        # 项目已使用空间：更新data_dict.get("file_size")单位是字节
        request.tracer.project.user_space += data_dict.get("file_size")
        request.tracer.project.save()

        result = {
            "id": instance.id,
            "name": instance.name,
            "file_size": instance.file_size,
            "username": instance.update_user.username,
            'datetime': instance.update_datetime.strftime("%Y{0}%m{1}%d{2} %H:%M").format("年", "月", "日"),
            "download_url": reverse("file_download", kwargs={"project_id": project_id, "file_id": instance.id})
            # "file_type": instance.get_file_type_display(),
        }
        return JsonResponse({"status": True, "data": result})
    return JsonResponse({"status": False, "data": "文件错误"})


def file_download(request, project_id, file_id):
    """
    下载文件
    :param request:
    :param project:
    :return:
    """
    # 文件内容
    # 响应头
    # 打开文件，获取文件的内容;去COS获取文件内容;
    file_object = models.FileRepository.objects.filter(id=file_id, project_id=project_id).first()
    res = requests.get(file_object.file_path)
    # 文件分块处理（适应大文件)
    data = res.iter_content()
    response = HttpResponse(data, content_type="application/octet-stream")
    from django.utils.encoding import  escape_uri_path
    # 设置响应头,浏览见到如下响应头就会去下载文件
    response["Content-Disposition"] = "attachment;filename={0}".format(escape_uri_path(file_object.name))
    return response
