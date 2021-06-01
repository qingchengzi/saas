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
    project_space = models.PositiveIntegerField(verbose_name="单项目空间",help_text="G")
    per_file_size = models.PositiveIntegerField(verbose_name="单文件大小", help_text="M")
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
    # 桶的名称
    bucket = models.CharField(verbose_name="cos桶", max_length=128)
    region = models.CharField(verbose_name="cos区域", max_length=32)

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


class Wiki(models.Model):
    """
    wiki表
    """
    project = models.ForeignKey(verbose_name="项目", to="Project")
    title = models.CharField(verbose_name="标题", max_length=32)
    content = models.TextField(verbose_name="内容")
    depth = models.IntegerField(verbose_name="深度", default=1)
    # 自己关联自己,to=self或者表名
    parent = models.ForeignKey(verbose_name="父文章", to="Wiki", null=True, blank=True, related_name="children")

    def __str__(self):
        return self.title


class FileRepository(models.Model):
    """文件库"""
    project = models.ForeignKey(verbose_name="项目", to="Project")
    file_type_choices = (
        (1, '文件'),
        (2, '文件夹')
    )
    file_type = models.SmallIntegerField(verbose_name="类型", choices=file_type_choices,
                                         )
    name = models.CharField(verbose_name="文件夹名称", max_length=32, help_text="文件/文件夹名")
    key = models.CharField(verbose_name="文件夹储存在COS中的KEY", max_length=128, null=True, blank=True)
    file_size = models.IntegerField(verbose_name="文件大小", null=True, blank=True)
    file_path = models.CharField(verbose_name="文件路径", max_length=255, null=True, blank=True)
    parent = models.ForeignKey(verbose_name="父级目录", to="self", related_name="child", null=True, blank=True)
    update_user = models.ForeignKey(verbose_name="最近更新者", to="UserInfo")
    update_datetime = models.DateTimeField(verbose_name="更新时间", auto_now=True)
