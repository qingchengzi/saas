#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/4 21:57 
# ide： PyCharm

from django.shortcuts import render


def index(request):
    return render(request, 'index.html')
