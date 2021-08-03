from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    # 电话号码字段
    mobile = models.CharField(max_length=11, unique=True, blank=False)
    # 头像
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
    # 个人简介
    user_desc = models.CharField(max_length=500, blank=True)

    # 修改认证的字段为 手机号
    USERNAME_FIELD = 'mobile'

    # 内部类 class Meta 用于给 model 定义元数据
    class Meta:
        db_table = 'tb_user'  # 修改默认的表名
        verbose_name = '用户信息'  # Admin后台显示
        verbose_name_plural = verbose_name  # Admin后台显示

    def __str__(self):
        return self.mobile

