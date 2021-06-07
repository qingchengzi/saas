#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/9 17:56 
# ide： PyCharm
from django.shortcuts import render


def dashboard(request, project_id):
    return render(request, "dashboard.html")


def statistics(request, project_id):
    return render(request, "statistics.html")
