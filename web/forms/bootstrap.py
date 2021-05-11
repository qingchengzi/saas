#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/3 21:26 
# ide： PyCharm


class BootStrapForm:
    bootstrap_class_exclude = []  # 那些不使用BooStrap样式放到这个列表,默认为空。

    # 重写init方法来给每个字段添加css样式属性等属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # 自定义那些需要使用BooStrap样式，那些不需要使用BooStrap。将不需要的放到bootstrap_class_exclude列表中
            # bootstrap_class_exclude列表为空说明所有都要添加样式
            if name in self.bootstrap_class_exclude:
                continue
            field.widget.attrs['class'] = "form-control"
            field.widget.attrs['placeholder'] = "请输入%s" % (field.label,)
