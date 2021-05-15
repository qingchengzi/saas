#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/12 21:00 
# ide： PyCharm

from django import forms

from web import models
from web.forms.bootstrap import BootStrapForm


class WkiModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Wiki
        exclude = ["project", "depth", ]

    # Models.Wiki中parent字段中自动生成下拉框里面的数据内容不是我们想要的，进行__init__方法重写
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 找到想要的字段把他绑定显示的数据重置
        # 数据 = 去数据库中获取当前项目所有的wiki标题
        total_data_list = [("", "请选择")]  # 下拉列表中添加请选择项
        data_list = models.Wiki.objects.filter(project=request.tracer.project).values_list("id", "title")
        total_data_list.extend(data_list)
        self.fields['parent'].choices = total_data_list
