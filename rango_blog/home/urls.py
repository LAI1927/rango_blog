# -*- coding=utf-8 -*-
# @Time : 2021/8/3 04:05
# @Author : YonglaiZhao
# @File: urls.py
# @Software: PyCharm

from django.urls import path
from home.views import IndexView, DetailView
urlpatterns = [
    path('', IndexView.as_view(), name='index'),  # Route of the HomePage
    path('detail/', DetailView.as_view(), name='detail'),  # Route of the detail view
]
