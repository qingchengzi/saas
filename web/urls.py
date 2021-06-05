#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/4/30 21:40 
# ide： PyCharm

from django.conf.urls import url, include
from web.views import account
from web.views import home
from web.views import project
from web.views import manage
from web.views import wiki
from web.views import file

urlpatterns = [
    url(r'^register/$', account.register, name='register'),
    url(r'^login/sms/$', account.login_sms, name='login_sms'),
    url(r'^login/$', account.login, name='login'),
    url(r'^image/code/$', account.image_code, name='image_code'),
    url(r'^send/sms/$', account.send_sms, name='send_sms'),
    url(r'^logout/$', account.logout, name='logout'),
    url(r'^index/$', home.index, name="index"),
    # 项目列表
    url(r'^project/list/$', project.project_list, name="project_list"),
    # 项目添加星标
    # 我创建的:/project/star/my/1
    # 我参与的:/project/star/join/1
    url(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name="project.star"),
    # 取消项目的星标
    url(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_unstar, name="project.unstar"),
    url(r'^manage/(?P<project_id>\d+)/', include([
        url(r'^dashboard/$', manage.dashboard, name="dashboard"),
        url(r'^issues/$', manage.issues, name="issues"),
        url(r'^statistics/$', manage.statistics, name="statistics"),

        url(r'^wiki/$', wiki.wiki, name="wiki"),
        url(r'^wiki/add/$', wiki.wiki_add, name="wiki_add"),
        url(r'^wiki/catalog/$', wiki.wiki_catalog, name="wiki_catalog"),
        url(r'^wiki/delete/(?P<wiki_id>\d+)/$', wiki.wiki_delete, name="wiki_delete"),
        url(r'^wiki/edit/(?P<wiki_id>\d+)/$', wiki.wiki_edit, name="wiki_edit"),
        url(r'^wiki/upload/$', wiki.wiki_upload, name="wiki_upload"),

        url(r'^file/$', file.file, name="file"),
        url(r'^file/delete/$', file.file_delete, name="file_delete"),
        url(r'^cos/credential/$', file.cos_credential, name="cos_credential"),
        url(r'^file/post/$', file.file_post, name="file_post"),
        # url(r'^file/download/(?P<file_id>\d+)/$', file.file_download, name='file_download'),
        url(r'^file/download/(?P<file_id>\d+)/$', file.file_download, name="file_download"),

        url(r'^setting/$', manage.setting, name="setting"),
    ], None, None)),

]
