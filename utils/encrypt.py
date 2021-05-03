#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/3 17:30 
# ide： PyCharm

import hashlib
from django.conf import settings


def md5(string):
    """
    MD5 加密
    :param string:
    :return:
    """
    hash_object = hashlib.md5(settings.SECRET_KEY.encode("utf-8"))
    hash_object.update(string.encode('utf-8'))
    return hash_object.hexdigest()
