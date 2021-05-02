#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/4/30 14:13 
# ide： PyCharm

"""
用户账号相关的功能：注册、短信、登录、注销
"""

from django.shortcuts import render
from web.forms.account import RegisterModelForm


def register(request):
    form = RegisterModelForm()
    return render(request, 'register.html', {'form': form})
