from django.db import models


# Create your models here.

class User(models.Model):
    # 用户名
    userName = models.CharField(max_length=20, blank=True)
    # 手机号
    userPhone = models.CharField(max_length=11, unique=True, blank=True)
    # 密码信息
    userPassword = models.CharField(max_length=30)
    # 头像信息
    avatar = models.ImageField(null=True, blank=True)
    # 简介信息
    user_desc = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'user'
