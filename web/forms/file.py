#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/24 20:58 
# ide： PyCharm

from django import forms
from django.core.exceptions import ValidationError
from web.forms.bootstrap import BootStrapForm
from web import models


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
