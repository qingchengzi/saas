#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/6/6 21:23 
# ide： PyCharm

from django.shortcuts import render
from web.forms.issues import IssuesModelForm


def issues(request, project_id):
    form = IssuesModelForm()
    return render(request, "issues.html", {"form": form})
