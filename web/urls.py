#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/4/30 21:40 
# ide： PyCharm

from django.conf.urls import url
from web.views import account

urlpatterns = [
    url(r'^register/$', account.register, name='register'),
]
