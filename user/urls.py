from django.urls import path
from user.views import *


urlpatterns = [

    # 注册视图函数路由
    path('register/', RegisterView.as_view(), name='register'),

    # 短信发送路由
    path('vercode/', VerCodeView.as_view(), name='verCode'),

    # 登录路由
    path('login/', LoginView.as_view(),name='login'),

    # 主页的路由
    # path('index/', UserCenterView.as_view(), name='index'),

]