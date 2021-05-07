from django.db import models


# Create your models here.

class UserInfo(models.Model):
    """
    用户表
    """
    username = models.CharField(verbose_name="用户名", max_length=32, db_index=True)  # db_index=True 创建索引
    email = models.EmailField(verbose_name="邮箱", max_length=32)
    mobile_phone = models.CharField(verbose_name="手机号", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=32)

    # price_policy = models.ForeignKey(verbose_name="价格策略", to="PricePolicy", null=True, blank=True)


class PricePolicy(models.Model):
    """
    价格策略表
    """
    category_choices = (
        (1, "免费版"),
        (2, "收费版"),
        (3, "其他")
    )
    category = models.SmallIntegerField(verbose_name="收费类型", default=2, choices=category_choices)  # 小正数
    title = models.CharField(verbose_name="标题", max_length=32)
    price = models.PositiveIntegerField(verbose_name="价格")  # 正整数

    project_num = models.PositiveIntegerField(verbose_name="项目数")
    project_member = models.PositiveIntegerField(verbose_name="项目成员")
    project_space = models.PositiveIntegerField(verbose_name="单项目空间")
    per_file_size = models.PositiveIntegerField(verbose_name="单文件大小(M)")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class Transaction(models.Model):
    """
    交易记录
    """
    status_choice = (
        (1, "未支付"),
        (2, "已支付")
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choice)
    order = models.CharField(verbose_name="订单号", max_length=64, unique=True)  # 唯一索引
    user = models.ForeignKey(verbose_name="用户", to="UserInfo")
    price_policy = models.ForeignKey(verbose_name="价格策略", to="PricePolicy")
    count = models.IntegerField(verbose_name="数量(年)", help_text="0表示无期限")
    price = models.IntegerField(verbose_name="实际支付价格")
    start_datetime = models.DateTimeField(verbose_name="开始时间", null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)

    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class Project(models.Model):
    """
    项目表
    """
    COLOR_CHOICES = (
        (1, "#56b8eb"),
        (2, "#f28033"),
        (3, "#ebc656"),
        (4, "#a2d148"),
        (5, "#20BFA4"),
        (6, "#7461c2"),
        (7, "#20bfa3"),
    )

    name = models.CharField(verbose_name="项目表", max_length=32)
    color = models.SmallIntegerField(verbose_name="颜色", choices=COLOR_CHOICES, default=1)
    desc = models.CharField(verbose_name="项目描述", max_length=255, null=True, blank=True)
    user_space = models.IntegerField(verbose_name="项目已使用空间", default=0)
    star = models.BooleanField(verbose_name="星标", default=False)

    # 暂未使用到
    # bucket = models.CharField(verbose_name="腾讯对象存储桶", max_length=128)
    # region = models.CharField(verbose_name="腾讯对象存储桶区域", max_length=32)

    join_count = models.SmallIntegerField(verbose_name="参与人数", default=1)
    creator = models.ForeignKey(verbose_name="创建者", to="UserInfo")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class ProjectUser(models.Model):
    """
    项目参与者
    """
    user = models.ForeignKey(verbose_name="用户", to="UserInfo")
    project = models.ForeignKey(verbose_name="项目", to="Project")
    # invitee = models.ForeignKey(verbose_name="邀请者", to="UserInfo")
    star = models.BooleanField(verbose_name="星标", default=False)
    create_datetime = models.DateTimeField(verbose_name="加入时间", auto_now_add=True)