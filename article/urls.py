from django.urls import path
from article.views import *

urlpatterns = [
    # 文章详情路由
    # path('detail/', DetailView.as_view(), name='detail'),
    # 写博客
    path('writeblog/', WriteBlogView.as_view(), name='writeblog'),
    # 文章列表
    path('index/',IndexView.as_view(),name = 'index'),
    # 文章详情
    path('detail/',DetailView.as_view(),name='detail')

]