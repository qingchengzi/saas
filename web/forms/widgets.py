#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/9 15:26 
# ide： PyCharm

from django.forms import RadioSelect


class ColorRadioSelect(RadioSelect):
    """
    自定义插件
    """
    template_name = 'widgets/color_radio/radion.html'
    option_template_name = 'widgets/color_radio/radio_option.html'
