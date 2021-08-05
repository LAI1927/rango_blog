# -*- coding=utf-8 -*-
# @Time : 2021/8/2 21:13
# @Author : YonglaiZhao
# @File: urls.py
# @Software: PyCharm

from django.urls import path
from users.views import RegisterView, ImageCodeView, SmsCodeView, LoginView, LogoutView, ForgetPasswordView, UserCenterView, WriteBlogView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('imagecode/', ImageCodeView.as_view(), name='imagecode'),  # Route of image verification code
    path('smscode/', SmsCodeView.as_view(), name='smscode'),  # send a text message
    path('login/', LoginView.as_view(), name='login'),  # Login routing
    path('logout/', LogoutView.as_view(), name='logout'),  # Sign out
    path('forgetpassword/', ForgetPasswordView.as_view(), name='forgetpassword'),  # forget the password
    path('center/', UserCenterView.as_view(), name='center'),  # Personal center
    path('writeblog/', WriteBlogView.as_view(), name='writeblog'),  # Route of writing blog
]
