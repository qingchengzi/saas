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
            "assign": forms.Select(attrs={"class": "selectpicker", "data-live-search": "true"}),
            # 关注着是多选:"data-actions-box": "true",多选和单选
            "attention": forms.SelectMultiple(
                attrs={
                    "class": "selectpicker",
                    "data-live-search": "true",
                    "data-actions-box": "true",
                }),
            "parent": forms.Select(attrs={"class": "selectpicker", "data-live-search": "true"}),  # 父问题下拉菜单添加搜索
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 新建问题弹窗中数据初始化的处理
        # 1、获取当前项目的所有问题类型(必选项不能为空)
        self.fields["issues_type"].choices = models.IssuesType.objects.filter(
            project=request.tracer.project).values_list(
            "id", "title")
        # 2、获取当前项目的所有模块(非必选项)
        module_list = [("", "没有选择任何项"), ]  # 下拉菜单提供【没有选择任何选项】的条目
        module_object_list = models.Module.objects.filter(project=request.tracer.project).values_list()
        module_list.extend(module_object_list)
        self.fields["module"].choices = module_list

        # 3、指派和关注者
        # 数据库找到当前项目的参与者 和 创建者
        total_user_list = [
            (request.tracer.project.creator_id, request.tracer.project.creator.username), ]  # 当前创建者的id和姓名
        project_user_list = models.ProjectUser.objects.filter(project=request.tracer.project).values_list("user_id",
                                                                                                          "user__username")  # 所有参与者
        total_user_list.extend(project_user_list)
        self.fields["assign"].choices = [("", "没有选择任何项")] + total_user_list
        self.fields["attention"].choices = total_user_list

        # 4、父问题 当前项目已创建的所有问题，让用户进行选择 ,严谨写法
        parent_list = [("", "没有选择任何项")]
        parent_object_list = models.Issues.objects.filter(project=request.tracer.project).values_list("id", "subject")
        parent_list.extend(parent_object_list)
        self.fields["parent"].choices = parent_list


class IssuesReplyModelForm(forms.ModelForm):
    class Meta:
        model = models.IssuesReply
        fields = ['content', 'reply']


class InviteModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.ProjectInvite
        fields = ['period', 'count']
