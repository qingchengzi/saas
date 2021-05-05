#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/5 11:38 
# ide： PyCharm

import django
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saas.settings")
django.setup()

from web import models

models.UserInfo.objects.create(username="tian", email="tian@qq.com", mobile_phone="13800138000", password=123456)
