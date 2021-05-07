#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/6 22:19 
# ide： PyCharm

from django import forms
from django.core.exceptions import ValidationError

from web.forms.bootstrap import BootStrapForm
from web import models


class ProjectModeForm(BootStrapForm, forms.ModelForm):
    # 方式1：重写models中字段且新增属性
    # desc = forms.CharField(widget=forms.Textarea(attrs={"xx":12}))  # 重写desc因为在models.py中是CharField类型

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    class Meta:
        model = models.Project
        fields = ["name", "color", "desc"]
        # 方式2 重写models中字段且通过attrs参数为该字段新增属性
        widgets = {
            # "desc": forms.Textarea(attrs={"xx": 123})
            "desc": forms.Textarea
        }

    def clean_name(self):
        """项目校验"""
        name = self.cleaned_data['name']
        # 1、当前用户是否已创建过此项目(项目名是否已存在),必须是当前用户所以使用了creator？
        exists = models.Project.objects.filter(name=name, creator=self.request.tracer.user).exists()
        if exists:
            raise ValidationError("项目名已存在")
        # 2、当前用户是否还有额度进行创建项目?
        # 最多创建多少个项目? 当前用户已经创建多少个项目? 查询后进行判断。
        count = models.Project.objects.filter(creator=self.request.tracer.user).count()
        if count >= self.request.tracer.price_policy.project_num:
            raise ValidationError("项目个数超限，请购买套餐")
        return name
