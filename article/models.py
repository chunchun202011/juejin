from django.db import models
from django.utils import timezone
from mdeditor.fields import MDTextField

from user.models import User

# Create your models here.
class ArticleCategory(models.Model):
    '''
    文章类别
    '''
    # 分类标题
    cate = models.CharField(max_length=100,blank=True)
    # 分类的创建时间
    created = models.DateTimeField(default=timezone.now)

    # 返回分类标题
    def __str__(self):
        return self.cate

    # 修改表名
    class Meta:
        db_table='category'

class Article(models.Model):
    '''
    作者id
    作者名
    作者头像

    文章标题
    封面地址
    文章类别
    文章摘要
    文章内容
    文章阅读量
    文章点赞量
    文章评论量
    发布时间

    '''

    # 作者信息,从这里链接user表可以取出作者名、作者头像信息
    # 作者id,默认连接User表的主键id
    authorId = models.ForeignKey(User, on_delete=models.CASCADE, db_column='authorId')
    # 作者名
    # authorName = models.ForeignKey(User.userName,on_delete=models.CASCADE,null=True)
    # # 作者头像
    # authorImg = models.ForeignKey(User.avatar,on_delete=models.CASCADE,null=True)
    # 建立数据库进行存储时，外键只能连接主键，在后续连接中搜索出展示即可
    authorName = models.CharField(max_length=20,null=True)
    authorImg = models.ImageField(null=True,blank=True)


    # 文章id
    articleId = models.AutoField(primary_key=True)
    # 文章标题
    title = models.CharField(max_length=100,blank=True)
    # 封面地址
    imgPath = models.ImageField(upload_to='article/%Y%m%d', blank=True)
    # 文章类别Id
    # 分类反向获取文章信息：取名为article,可由分类反向获取文章信息
    cateId = models.ForeignKey(ArticleCategory, null=True,  blank=True, on_delete=models.CASCADE, related_name='article', db_column='cateId')
    # 文章类别
    cate = models.CharField(max_length=100, blank=True)
    # 文章摘要
    abstract = models.TextField()
    # 文章内容
    content = MDTextField()  # 保存md
    # 文章阅读量
    view = models.PositiveIntegerField()
    # 文章点赞量
    like = models.PositiveIntegerField(default=0)
    # 文章评论量
    comment = models.PositiveIntegerField(default=0)
    # 发布时间
    releaseTime = models.DateTimeField(default=timezone.now)

    # 修改表名
    class Meta:
        db_table = 'article'

    # 返回标题名
    def __str__(self):
        return self.title



