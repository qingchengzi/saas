#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/24 20:58 
# ide： PyCharm

from django import forms
from django.core.exceptions import ValidationError
from web.forms.bootstrap import BootStrapForm
from web import models

from utils.tencent.cos import check_file


class FolderModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.FileRepository
        fields = ['name']

    def __init__(self, request, parent_object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_object = parent_object

    def clean_name(self):
        """
        新增文件夹是否重名
        :return:
        """
        name = self.cleaned_data["name"]
        # 数据库判断当前目录此文件夹是否已存在

        # if self.parent_object:
        #     models.FileRepository.objects.filter(file_type=2, name=name, project=self.request.tracer.project,
        #                                          parent=self.parent_object)
        # else:
        #     models.FileRepository.objects.filter(file_type=2, name=name, project=self.request.tracer.project,
        #                                          parent__isnull=True)
        # 简写
        queryset = models.FileRepository.objects.filter(file_type=2, name=name, project=self.request.tracer.project)
        if self.parent_object:
            exists = queryset.filter(parent=self.parent_object).exists()
        else:
            exists = queryset.filter(parent__isnull=True).exists()
        if exists:
            raise ValidationError("文件夹已存在")
        return name


class FileModelForm(forms.ModelForm):
    """
    验证前端传入的数据是否正确,防止恶意程序构造POST请求，不断发送请求，然后不断保存到数据库
    这里先对文件的大小和ETag进行校验。
    """
    etag = forms.CharField(label="ETag")

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    class Meta:
        model = models.FileRepository
        exclude = ["project", "file_type", "update_user", "update_datetime"]

    def clean_file_path(self):
        print("https://{0}".format(self.cleaned_data.get("file_path")))
        return "https://{0}".format(self.cleaned_data.get("file_path"))

    """
    加验证会慢一点，这里先注释，需要的时候开启即可
    def clean(self):
        # etag的目的，向COS校验文件是否合法
        key = self.cleaned_data.get("key")
        etag = self.cleaned_data.get("etag")
        size = self.cleaned_data.get("size")
        if not key or not etag:
            return self.cleaned_data
        # COS校验文件是否合法
        # 通过腾讯COS中的SDK功能
        from qcloud_cos.cos_exception import CosServiceError
        try:
            result = check_file(self.request.tracer.project.bucket, self.request.tracer.project.region, key)
        except CosServiceError as e:
            self.add_error("key", "文件不存在")
            return self.cleaned_data
        cos_etag = result.get("ETag")
        if etag != cos_etag:
            self.add_error("etag", "ETag错误")
        cos_length = result.get("Content-Length")
        if int(cos_length) != size:
            self.add_error("size", "文件大小错误")
        return self.cleaned_data
    """