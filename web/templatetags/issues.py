#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/6/11 23:21 
# ide： PyCharm

from django.template import Library
from web import models
from django.urls import reverse  # url进行反向解析用

register = Library()


@register.simple_tag()
def string_just(num):
    if num < 100:
        num = str(num).rjust(3, "0")
    return "#{0}".format(num)
