import random
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.conf import settings

from django_redis import get_redis_connection

from web import models
from utils.tencent.sms import send_sms_single
from utils import encrypt
from web.forms.bootstrap import BootStrapForm


class RegisterModelForm(BootStrapForm, forms.ModelForm):
    # CharField(widget=forms.PasswordInput())参数中加载插件后，密文显示密码
    password = forms.CharField(
        label="密码",
        min_length=8,
        max_length=64,
        error_messages={
            'mig_length': "密码长度不能小于8个字符",
            'max_length': "密码长度不能大于64个字符"
        },
        widget=forms.PasswordInput())
    # 新增确认密码字段,数据库中是没有该字段
    confirm_password = forms.CharField(
        label="重复密码",
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': "重复密码长度不能小于8个字符",
            'max_length': "重复密码长度不能大于64个字符"
        },
        widget=forms.PasswordInput())
    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput())
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])

    class Meta:
        model = models.UserInfo
        # fields = "__all__"   默认在html中的标签的排序
        # 自定义html页面中，标签展示的顺序
        fields = ["username", "email", "password", "confirm_password", "mobile_phone", "code"]

    def clean_username(self):
        """
        用户名不能重名的局部钩子
        :return:
        """
        username = self.cleaned_data['username']
        exists = models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError("用户名已存在")
        return username

    def clean_email(self):
        """
        邮箱不能重复
        :return:
        """
        email = self.cleaned_data['email']
        exists = models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError("邮箱已存在")
        return email

    def clean_password(self):
        pwd = self.cleaned_data['password']
        # 加密 & 返回
        return encrypt.md5(pwd)

    def clean_confirm_password(self):
        """
        获取用户输入的两次密码
        :return:
        """
        pwd = self.cleaned_data.get('password')
        confirm_pwd = encrypt.md5(self.cleaned_data['confirm_password'])
        if pwd != confirm_pwd:
            raise ValidationError("两次密码不一致")
        return confirm_pwd

    def clean_mobile_phone(self):
        """手机号是否已经注册的校验"""
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError("手机号已注册")
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get("mobile_phone")
        if not mobile_phone:
            return code
        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError("验证码失效或未发送，请重新发送")
        redis_str_code = redis_code.decode("utf-8")
        if code.strip() != redis_str_code:
            raise ValidationError("验证码错误，请重新输入")
        return code


class SendSmsForm(forms.Form):
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        """手机号校验的钩子"""
        mobile_phone = self.cleaned_data['mobile_phone']  # 用户提交过来的手机号
        # 判断短信模板是否有问题
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        if not template_id:
            raise ValidationError("短信模板错误")
        # 校验数据库是否已有手机号
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if tpl == "login":
            if not exists:
                raise ValidationError("手机号不存在")
        else:
            # 校验数据库中是否已有手机号
            if exists:
                raise ValidationError("手机号已存在")
        # 发短信 & 写入redis
        code = random.randrange(1000, 9999)
        # 发送短信
        # sms = send_sms_single(mobile_phone, template_id, [code, ])
        # if sms['result'] != 0:
        #     raise ValidationError("短信发送失败,{0}".format(sms['errmsg']))
        # 验证码写入redis (django-redis)
        # 获取redis连接
        print("验证码是code:", code)
        conn = get_redis_connection()
        conn.set(mobile_phone, code, ex=60)
        return mobile_phone


class LoginSMSForm(BootStrapForm, forms.Form):
    """
    登录
    """
    mobile_phone = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])

    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput())

    def clean_mobile_phone(self):
        """
        如果手机号存在，将当前用户对象返回
        :return:
        """
        mobile_phone = self.cleaned_data["mobile_phone"]
        # exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        user_object = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        if not user_object:
            raise ValidationError("手机号不存在")
        return user_object

    def clean_code(self):
        """
        校验验证码
        :return:
        """
        code = self.cleaned_data['code']
        user_object = self.cleaned_data.get("mobile_phone")
        # 手机号不存在，验证码无需再校验
        if not user_object:
            return code
        conn = get_redis_connection()
        redis_code = conn.get(user_object.mobile_phone)
        if not redis_code:
            raise ValidationError("验证码失效或未发送，请重新发送")
        redis_str_code = redis_code.decode("utf-8")
        if code.strip() != redis_str_code:
            raise ValidationError("验证码错误，请重新输入")
        return code


class LoginForm(BootStrapForm, forms.Form):
    """
    用户名和密码登录页面
    """
    # username = forms.CharField(label="用户名")
    username = forms.CharField(label="手机号或邮箱")
    # password = forms.CharField(label="密码", widget=forms.PasswordInput()) # 输入错误密码后会自动清空原密码
    password = forms.CharField(label="密码", widget=forms.PasswordInput(render_value=True))  # 输入错误密码后会保存原密码
    code = forms.CharField(label="图片验证码")

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_password(self):
        pwd = self.cleaned_data['password']
        # 加密 & 返回
        return encrypt.md5(pwd)

    def clean_code(self):
        """
        校验图片验证码是否正确
        :return:
        """
        # 读取用户输入的验证码
        code = self.cleaned_data['code']
        # session中获取自己的验证码
        session_code = self.request.session.get("image_code")
        if not session_code:
            raise ValidationError("验证码已过期，请重新获取")
        if code.strip().upper() != session_code.strip().upper():
            raise ValidationError("验证码输入错误")
        return code
