#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/6/6 22:41 
# ide： PyCharm

from django import forms
from web.forms.bootstrap import BootStrapForm
from web import models


class IssuesModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Issues
        exclude = ["project", "creator", "create_datetime", "latest_update_datetime"]
        widgets = {
            # 指派单选标签添加bootstrap-select插件样式。让bootstrap-select插件生效的方法就是设置前端标签中添加class=selectpicker属性
            # class = selectpicker样式,搜索功能："data-live-seach":"true"
            "assign": forms.Select(attrs={"class": "selectpicker","data-live-search": "true"}),
            # 关注着是多选:"data-actions-box": "true",多选和单选
            "attention": forms.SelectMultiple(
                attrs={
                    "class": "selectpicker",
                    "data-live-search": "true",
                    "data-actions-box": "true",
                }), }
