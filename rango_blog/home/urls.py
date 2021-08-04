# -*- coding=utf-8 -*-
# @Time : 2021/8/3 04:05
# @Author : YonglaiZhao
# @File: urls.py
# @Software: PyCharm

from django.urls import path
from home.views import IndexView, DetailView
urlpatterns = [
    # 首页的路由
    path('', IndexView.as_view(), name='index'),  # 详情视图的路由
    path('detail/', DetailView.as_view(), name='detail'),  # 详情视图的路由
]
