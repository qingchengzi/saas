#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/5 18:16 
# ide： PyCharm

from scripts import base

from web import models


def run():
    exists = models.PricePolicy.objects.filter(category=1, title="个人免费版").exists()
    if not exists:
        models.PricePolicy.objects.create(
            category=1,
            title="个人免费版",
            price=0,
            project_num=3,
            project_space=20,
            project_member=2,
            per_file_size=5
        )


if __name__ == '__main__':
    run()
