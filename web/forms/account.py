#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/2 13:52 
# ide： PyCharm

from django import forms
from web import models
from django.core.validators import RegexValidator


class RegisterModelForm(forms.ModelForm):
    # 重写models.UserInfo中的mobile_phone手机号属性，添加正则匹配条件
    # forms中没有手机号码的字段，所以需要validators参数来定义手机号码的正则表达式
    # RegexValidator()对象接收两个参数，第一个是正则表达式，第二个是如果正则匹配不到时报错信息
    mobile_phone = forms.CharField(label="手机号", validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9]\d{9}$)', "手机号码格式错误"), ])
    # CharField(widget=forms.PasswordInput())参数中加载插件后，密文显示密码
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput())
    # 新增确认密码字段,数据库中是没有该字段
    confirm_password = forms.CharField(
        label="重复密码",
        widget=forms.PasswordInput())
    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput())

    class Meta:
        model = models.UserInfo
        # fields = "__all__"   默认在html中的标签的排序
        # 自定义html页面中，标签展示的顺序
        fields = ["username", "email", "password", "confirm_password", "mobile_phone", "code"]

    # 重写init方法来给每个字段添加css样式属性等属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control"
            field.widget.attrs['placeholder'] = "请输入%s" % (field.label,)
