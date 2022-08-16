import logging

from django.core.paginator import EmptyPage
from django.urls import reverse

from user.models import User

logger = logging.getLogger('django')
from django.http import HttpResponseBadRequest, request, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
import markdown
from django.shortcuts import render, get_object_or_404

# Create your views here.
# 写博客
from article.models import ArticleCategory, Article


class WriteBlogView(View):

    def get(self,request):
        # 查询所有分类模型
        categories = ArticleCategory.objects.all()
        context = {
            'categories':categories
        }
        return render(request,'write_blog.html',context=context)

    def post(self,request):
        '''
        1.接收数据
        2.验证数据
        3.数据入库
        4.跳转到指定页面（暂时首页）
        :param request:
        :return:
        '''
        # 1.接收数据
        imgPath = request.FILES.get('imgPath')
        title = request.POST.get('title')
        cate = request.POST.get('cate')
        abstract = request.POST.get('abstract')
        content = request.POST.get('content')
        author = request.user

        # 2.验证数据
        if not all([title,abstract,cate,content]):
            return HttpResponseBadRequest('参数不全')
        # 3.数据入库
        try:
            article = Article.objects.create(
                author = author,
                imgPath=imgPath,
                title = title,
                cate = cate,
                abstract=abstract,
                content=content
            )
        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest('发布失败，请稍后再试')
        # 4.跳转到指定页面（暂时首页）
        return redirect(reverse('/user/index/'))


# 文章详情
class DetailView(View):

    def get(self, request):
        '''
        1.接收文章id信息
        2.根据文章id进行文章数据的查询
        3.查询分类数据
        4.组织模板数据
        :param request:
        :return:
        '''
        # 1.接收文章id信息
        id = request.GET.get('id')
        # 2.根据文章id进行文章数据的查询
        try:
            article = Article.objects.get(id=id)
        except Article.DoesNotExist:
            pass
            # 将markdown语法渲染成html样式
            article.content = markdown.markdown(article.content,
            extensions=[
                # 包含 缩写、表格等常用扩展
               'markdown.extensions.extra',
               # 语法高亮扩展
               'markdown.extensions.codehilite',
                         ])

        context = {"article": article}
        # 3. 查询分类数据
        categories = ArticleCategory.objects.all()
        # 4.组织模板数据
        context = {
            'categories': categories,
            # 'category': article.category,
            # 'article:': article
        }
        return render(request, 'detail.html', context=context)

# 文章分页
class IndexView(View):
    def get(self,request):

        '''
        1.获取所有分类信息
        2.接收用户点击的分类id
        3.根据分类id进行分类的查询
        4.获取分页参数
        5.根据分页信息查询文章数据
        6.创建分页器
        7.进行分页处理
        8.组织数据传递给模板

        '''

        # 1. 获取所有分类信息
        categories = ArticleCategory.objects.all()
        # 2. 接收用户点击的分类id
        cateId = request.GET.get('id', 1)
        # 3.根据分类id进行分类的查询
        try:
            # category为查询到的某一分类名称
            category = ArticleCategory.objects.get(id=cateId)
        except ArticleCategory.DoesNotExist:
            return HttpResponseNotFound('没有此分类')
        # 4.  获取分页参数
        page_num = request.GET.get('page_num',1)
        page_size = request.GET.get('page_size',10)
        # 5. 根据分页信息查询文章数据
        # 根据某一分类查询文章
        articles = Article.objects.filter(cate=category)
        # 6. 创建分页器
        from django.core.paginator import  Paginator
        paginator = Paginator(articles,per_page=page_size)
        # 7. 进行分页处理
        try:
            page_articles = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')
        # 总页数
        total_page = paginator.page(page_num)
        # 8. 组织数据传递给模板
        context={
            'categories':categories,
            'category':category,
            'articles':page_articles,
            'total_page':total_page,
            'page_num':page_num
        }
        return render(request,'index.html',context=context)

# 博客详情页面
class DetailView(View):
    def get(self,request):
        '''
        1.接收文章id
        2.根据文章id查数据
        3.查询分类数据
        4.组织模板数据
        :param request:
        :return:
        '''
        # 1.接收文章id
        articleId = request.GET.get('id')
        # 2.根据文章id查数据
        try:
            article = Article.objects.get(articleId=articleId)
        except Article.DoesNotExist:
            pass
        # 3.查询分类数据
        categories = ArticleCategory.objects.all()
        # 4.组织模板数据
        article = Article.objects.get(articleId=articleId)
        context = {
            'categories':categories,
            'category':article.cateId,  # 文章类别
            'article':article

        }
        return render(request,'detail.html',context=context)