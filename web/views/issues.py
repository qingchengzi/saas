#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/6/6 21:23
# ide： PyCharm

import json
import datetime

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
from django.urls import reverse

from web.forms.issues import IssuesModelForm, InviteModelForm
from web import models

from utils.pagination import Pagination  # 自定义的分页主键
from utils.encrypt import uid  # 随机字符串


class CheckFilter:
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            ck = ""
            # 如果当前用户请求的URL中status和当前循环key相等 ck="checked"
            value_list = self.request.GET.getlist(self.name)  # 用在url上传过来的status
            if key in value_list:
                ck = "checked"
                value_list.remove(key)  # 移除key
            else:
                value_list.append(key)
            # 为自己生成URL
            # 在当前URL的基础上去增加一项
            query_dict = self.request.GET.copy()  # 包含了status=1&age=19
            # print(query_dict)
            query_dict._mutable = True  # 默认不允许修改query_dict,修改query_dict._mutable = True后，通过 query_dict.setlist()来修改
            query_dict.setlist(self.name,
                               value_list)
            if "page" in query_dict:  # 获取的参数有分页存在
                query_dict.pop("page")
            # 去除url中有翻页时点击筛选后，出现？问题
            param_url = query_dict.urlencode()
            if param_url:
                url = "{0}?{1}".format(self.request.path_info,
                                       query_dict.urlencode())  # urlencode()生成url参数的格式：status=1&status=2&status=3
            else:
                url = self.request.path_info
            tpl = '<a class="cell" href="{url}"><input type="checkbox" {ck} /><label>{text}</label></a>'
            html = tpl.format(url=url, ck=ck, text=text)

            yield mark_safe(html)


class SelectFilter:
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        yield mark_safe("<select class='select2' multiple='multiple' style='width:100%;'>")
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            selected = ""
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                selected = "selected"
                value_list.remove(key)
            else:
                value_list.append(key)

            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            if "page" in query_dict:
                query_dict.pop("page")
            param_url = query_dict.urlencode()
            if param_url:
                url = "{0}?{1}".format(self.request.path_info,
                                       query_dict.urlencode())  # urlencode()生成url参数的格式：status=1&status=2&status=3
            else:
                url = self.request.path_info

            html = "<option value= '{url}' {selected}  >{text}</option></select>".format(url=url, selected=selected,
                                                                                         text=text)
            yield mark_safe(html)
        yield mark_safe("</select>")


def issues(request, project_id):
    if request.method == "GET":
        # 根据URL做筛选,筛选条件(用户通过GET传过来的参数实现)
        # ?status=1&status2&issues_type=1
        allow_filter_name = ["issues_type", "status", "priority", "assign", "attention"]
        condition = {}
        for name in allow_filter_name:
            value_list = request.GET.getlist(name)  # getlist获取所有的值
            if not value_list:
                continue
            condition["{0}__in".format(name)] = value_list
        """
        condition = {
            "status__in":[1,2],
            "issues_type":[1,]
        }
        """

        # 分页获取数据
        queryset = models.Issues.objects.filter(project_id=project_id).filter(**condition)
        page_object = Pagination(
            current_page=request.GET.get("page"),  # 当前页面
            all_count=queryset.count(),  # 数据库共多少条数据
            base_url=request.path_info,
            query_params=request.GET,  # 参数
            per_page=50,  # 每页显示50条数据，不写默认30条，这里是为了测试
        )
        issues_object_list = queryset[page_object.start:page_object.end]

        form = IssuesModelForm(request)
        # 问题类型
        project_issues_type = models.IssuesType.objects.filter(
            project_id=project_id).values_list("id", "title")
        project_total_user = [(request.tracer.project.creator_id, request.tracer.project.creator.username,)]
        join_user = models.ProjectUser.objects.filter(project_id=project_id).values_list("user_id",
                                                                                         "user__username")
        project_total_user.extend(join_user)

        # 邀请码
        invite_form = InviteModelForm()
        context = {
            "form": form,
            "invite_form": invite_form,
            "issues_object_list": issues_object_list,
            "page_html": page_object.page_html(),
            "filter_list": [
                {"title": "问题类型", "filter": CheckFilter("issues_type", project_issues_type, request), },
                {"title": "状态", "filter": CheckFilter("status", models.Issues.status_choices, request), },
                {"title": "优先级", "filter": CheckFilter("priority", models.Issues.priority_choices, request), },
                {"title": "指派者", "filter": SelectFilter("assign", project_total_user, request), },
                {"title": "关注者", "filter": SelectFilter("attention", project_total_user, request), },

            ]
        }
        return render(request, "issues.html", context)

    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        # 添加问题
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def issues_detail(request, project_id, issues_id):
    """
    编辑问题页面
    :param request:
    :param project_id:
    :param issues_id:
    :return:
    """
    issues_object = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()

    form = IssuesModelForm(request, instance=issues_object)
    return render(request, "issues_detail.html", {"form": form, "issues_object": issues_object})


@csrf_exempt
def issues_record(request, project_id, issues_id):
    """初始化操作记录"""
    # 判断是否可以评论和是否可以操作这个问题
    if request.method == "GET":
        reply_list = models.IssuesReply.objects.filter(issues_id=issues_id, issues__project=request.tracer.project)
        # 将querSet转换为json格式
        data_list = []
        for row in reply_list:  # 构造页面上需要展示的字段
            data = {
                "id": row.id,
                "reply_type_text": row.get_reply_type_display(),
                "content": row.content,
                "creator": row.creator.username,
                "datetime": row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                "parent_id": row.reply_id
            }
            data_list.append(data)
        return JsonResponse({"status": True, "data": data_list})

    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.issues_id = issues_id
        form.instance.reply_type = 2
        form.instance.creator = request.tracer.user
        instance = form.save()
        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.username,
            'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': instance.reply_id
        }

        return JsonResponse({'status': True, 'data': info})
    return JsonResponse({"status": False, "error": form.errors})


@csrf_exempt
def issues_change(request, project_id, issues_id):
    issues_object = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()
    post_dict = json.loads(request.body.decode("utf-8"))
    name = post_dict.get("name")
    value = post_dict.get("value")
    print(post_dict)
    field_object = models.Issues._meta.get_field(name)  # 数据库字段是否为空的对象

    def create_reply_record(content):
        # 将数据添加到数据库，返回新增数据的对象
        new_object = models.IssuesReply.objects.create(
            reply_type=1,
            issues=issues_object,
            content=change_record,
            creator=request.tracer.user,
        )
        new_reply_dict = {
            "id": new_object.id,
            "reply_type_text": new_object.get_reply_type_display(),
            "content": new_object.content,
            "creator": new_object.creator.username,
            "datetime": new_object.create_datetime.strftime("%Y-%m-%d %H:%M"),
            "parent_id": new_object.reply_id
        }
        return new_reply_dict

    # 1.数据库字段更新,先进行分类，分成如下4类然后对每个分类进行单独处理。这样做的目的是：防止黑客非法修改字段
    # 1.1 文本 ,文本类型的字段
    if name in ["subject", "desc", "start_date", "end_date"]:
        if not value:  # 用户输入为空
            if not field_object.null:  # 数据库不允许为空
                return JsonResponse({"status": False, "error": "您选择的值不能为空"})
            setattr(issues_object, name, None)
            issues_object.save()
            # 记录:xx更新为空
            # 构造变更记录，这里的记录为空
            change_record = "{0}更新为空".format(field_object.verbose_name)
        else:
            setattr(issues_object, name, value)
            issues_object.save()
            # 记录：xx更新为value
            # 构造变更记录
            change_record = "{0}更新为:{1}".format(field_object.verbose_name, value)

        return JsonResponse({"status": True, "data": create_reply_record(change_record)})
    # 1.2 FK字段处理(指派需要判断是否是创建者或者参与者)
    if name in ["issues_type", "module", "parent", "assign"]:
        if not value:  # 用户选择为空
            if not field_object.null:  # 数据库中不允许为空
                return JsonResponse({"status": False, "error": "您选择的值不能为空"})
            # 数据库允许为空
            setattr(issues_object, name, None)  # 找到字段设置None
            issues_object.save()
            change_record = "{0}更新为空".format(field_object.verbose_name)
        else:  # 用户输入不为空
            if name == "assign":  # 指派的话需要特殊处理,只有项目的创建者和参与者才能被指派
                # 是否是项目的创建者
                if value == str(request.tracer.project.creator_id):  # 当前项目创建者的ID和用户提交用户ID对比,如果相等就是创建者
                    instance = request.tracer.project.creator
                else:  # 是否是项目的参与者
                    project_user_object = models.ProjectUser.objects.filter(project_id=project_id,
                                                                            user_id=value).first()
                    if project_user_object:  # 是参与者
                        instance = project_user_object.user
                    else:  # 不是创建者也不是参与者
                        instance = None
                if not instance:
                    return JsonResponse({"status": False, "error": "您选择的值不存在"})

                setattr(issues_object, name, instance)
                issues_object.save()
                change_record = "{0}更新为:{1}".format(field_object.verbose_name,
                                                    str(instance))  # str(instance) 取模型对象instance中__str__中返回的值

            else:
                # 条件判断:用户输入的值，是自己的值
                instance = field_object.rel.model.objects.filter(id=value,
                                                                 project_id=project_id).first()  # project_id必须是当前项目的，别人的不行
                if not instance:
                    return JsonResponse({"status": False, "error": "您选择的值不存在"})

                setattr(issues_object, name, instance)
                issues_object.save()
                change_record = "{0}更新为:{1}".format(field_object.verbose_name,
                                                    str(instance))  # str(instance) 取模型对象instance中__str__中返回的值

        # 将数据添加到数据库，返回新增数据的对象
        return JsonResponse({"status": True, "data": create_reply_record(change_record)})
    # 1.3 choices字段
    if name in ["priority", "status", "mode"]:
        selected_text = None
        for key, text in field_object.choices:  # choices是一个元祖
            if str(key) == value:
                selected_text = text
        if not selected_text:
            return JsonResponse({"status": False, "error": "您选择的值不存在"})
        setattr(issues_object, name, value)  # 设置到数据库
        issues_object.save()
        change_record = "{0}更新为:{1}".format(field_object.verbose_name, selected_text)
        return JsonResponse({"status": True, "data": create_reply_record(change_record)})
    # 1.4 M2M多对多字段 关注者
    if name in ["attention"]:
        # 用户提交过来的关注者格式:{"name":"attention","value":[1,2,3]}
        if not isinstance(value, list):  # 是否是列表类型
            return JsonResponse({"status": False, "error": "数据格式错误"})
        # 关注者可以为空，所有需要考虑为空情况
        if not value:
            issues_object.attention.set([])  # 第三张表的关联关系置空
            issues_object.save()
            change_record = "{0}更新为空".format(field_object.verbose_name)
        else:  # values = [1,2,3,4] 判断values中的id是否是项目成员(创建者，参与者)
            # 获取当前项目的所有成员
            user_dict = {str(request.tracer.project.creator_id): request.tracer.project.creator.username}
            project_user_list = models.ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username
            username_list = []
            for user_id in value:
                username = user_dict.get(str(user_id))
                if not username:
                    return JsonResponse({"status": False, "error": "用户不存在请重新设置"})
                username_list.append(username)

            issues_object.attention.set(value)
            issues_object.save()
            change_record = "{0}更新为:{1}".format(field_object.verbose_name, ",".join(username_list))
        return JsonResponse({"status": True, "data": create_reply_record(change_record)})
    # 2.生成操作记录
    return JsonResponse({"status": False, "error": "非法操作"})


def invite_url(request, project_id):
    """
    生成邀请码
    :param request:
    :param project_id:
    :return:
    """
    form = InviteModelForm(data=request.POST)
    if form.is_valid():
        """
        1、创建随机的邀请码
        2、验证码保存到数据库
        3、限制：只有创建者才能邀请
        """
        if request.tracer.user != request.tracer.project.creator:  # 当前用户不是项目的创建者不能进行邀请
            form.add_error("period", "无权创建邀请码")  # 有效期下面提示
            return JsonResponse({"status": False, "error": form.errors})
        random_invite_code = uid(request.tracer.user.mobile_phone)
        form.instance.project = request.tracer.project
        form.instance.code = random_invite_code
        form.instance.creator = request.tracer.user
        form.save()

        # 将验证码返回给前段，前段页面上展示出来。
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,  # 获取http或者https
            host=request.get_host(),  # 主机IP和端口
            path=reverse("invite_join", kwargs={"code": random_invite_code})
            # 反向生成url格式 /invite/join/asdfadiqr-9asudfapsef/

        )
        return JsonResponse({"status": True, "data": url})

    return JsonResponse({"status": False, "error": form.errors})


def invite_join(request, code):
    """
    访问邀请码
    :param request:
    :param code:
    :return:
    """
    current_datetime = datetime.datetime.now()
    invite_object = models.ProjectInvite.objects.filter(code=code).first()
    if not invite_object:
        return render(request, "invite_join.html", {"error": "邀请码不存在"})
    if invite_object.project.creator == request.tracer.user:  # 邀请者等于当前登录的用户
        return render(request, "invite_join.html", {"error": "创建者无需在加入项目"})
    # 已经加入了
    exists = models.ProjectUser.objects.filter(project=invite_object.project, user=request.tracer.user).exists()
    if exists:
        return render(request, "invite_join.html", {"error": "已加入项目无需再加入"})
    # 最多允许的成员(要进入的项目的创建者的限制)
    # max_member = request.tracer.price_policy.project_member 当前登录用户

    # 当前项目的创建者：invite_object.project.creator
    # 是否已过期，如果过期则使用免费额度
    max_transaction = models.Transaction.objects.filter(user=invite_object.project.creator).order_by(
        "-id").first()  # 交易记录最大的值
    if max_transaction.price_policy.category == 1:  # 免费额度
        max_member = max_transaction.price_policy.project_member
    else:
        if max_transaction.end_datetime < current_datetime:  # 过期后只能使用免费额度
            free_object = models.PricePolicy.objects.filter(category=1).first()
            max_member = free_object.project_member
        else:  # 没有过期
            max_member = max_transaction.price_policy.project_member

    # 目前所有成员(没有包含创建者)
    # current_member = models.ProjectUser.objects.filter(project=invite_object.project).count()
    # 包含创建者和参与者
    current_member = models.ProjectUser.objects.filter(project=invite_object.project).count()
    current_member = current_member + 1
    if current_member >= max_member:
        return render(request, "invite_join.html", {"error": "项目成员超过限制,请升级套餐"})

    # 邀请码本身的判断
    # 邀请码是否过期

    # 截止时间 ,创建时间+有效期时间=截止时间
    limit_datetime = invite_object.create_datetime + datetime.timedelta(minutes=invite_object.period)
    if current_datetime > limit_datetime:
        return render(request, "invite_join.html", {"error": "邀请码已过期"})
    # 邀请数量限制
    if invite_object.count:  # 有数量限制
        if invite_object.use_count >= invite_object.count:
            return render(request, "invite_join.html", {"error": "邀请码数量已使用完"})
        invite_object.use_count += 1
        invite_object.save()

    # 无数量限制
    models.ProjectUser.objects.create(user=request.tracer.user, project=invite_object.project)
    # 项目表中参与人数更新
    invite_object.project.join_count += 1
    invite_object.project.save()
    return render(request, "invite_join.html", {'project': invite_object.project})
