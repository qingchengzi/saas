import random
from django.shortcuts import render, HttpResponse
from django import forms
from django.core.validators import RegexValidator  # 正则表达式

from utils.tencent.sms import send_sms_single

from django.conf import settings
from app01 import models


# Create your views here.

def send_sms(request):
    """发送短信实例"
       ?tpl=login --> 548762
       ?tpl=register --> 548760
       通过url中的tpl值来判断用户传过来的是登录还是注册
       注册：http://127.0.0.1:8000/send/sms/?tpl=register
       登录：http://127.0.0.1:8000/send/sms/?tpl=login
    """
    tpl = request.GET.get("tpl")
    template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
    if not template_id:
        return HttpResponse("模板不存在")

    code = random.randrange(1000, 9999)
    res = send_sms_single("13578786567", template_id, [code, ])
    print(res)
    if res["result"] == 0:
        return HttpResponse("成功")
    else:
        return HttpResponse(res["errmsg"])


class RegisterModelForm(forms.ModelForm):
    # 重写models.UserInfo中的mobile_phone手机号属性，添加正则匹配条件
    # forms中没有手机号码的字段，所以需要validators参数来定义手机号码的正则表达式
    # RegexValidator()对象接收两个参数，第一个是正则表达式，第二个是如果正则匹配不到时报错信息
    mobile_phone = forms.CharField(label="手机号", validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9]\d{9}$)', "手机号码格式错误"), ])
    # CharField(widget=forms.PasswordInput())参数中加载插件后，密文显示密码
    password = forms.CharField(label="密码", widget=forms.PasswordInput())
    # 新增确认密码字段,数据库中是没有该字段
    confirm_password = forms.CharField(label="重复密码", widget=forms.PasswordInput())
    code = forms.CharField(label="验证码")

    class Meta:
        model = models.UserInfo
        fields = "__all__"


def register(request):
    """
    注册功能实例
    :param request:
    :return:
    """
    form = RegisterModelForm()
    return render(request, "register.html", {"form": form})
