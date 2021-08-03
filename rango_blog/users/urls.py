# -*- coding=utf-8 -*-
# @Time : 2021/8/2 21:13
# @Author : YonglaiZhao
# @File: urls.py
# @Software: PyCharm

from django.urls import path
from users.views import RegisterView,ImageCodeView, SmsCodeView, LoginView, LogoutView, ForgetPasswordView, UserCenterView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('imagecode/', ImageCodeView.as_view(), name='imagecode'),
    path('smscode/', SmsCodeView.as_view(), name='smscode'),
    path('login/', LoginView.as_view(), name='login'),  # 登录路由
    path('logout/', LogoutView.as_view(), name='logout'),  # 退出登录
    path('forgetpassword/', ForgetPasswordView.as_view(), name='forgetpassword'),  # 忘记密码
    path('center/', UserCenterView.as_view(), name='center'),  # 个人中心
]
