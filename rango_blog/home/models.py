from django.db import models
from django.utils import timezone
from users.models import User


class ArticleCategory(models.Model):
    title = models.CharField(max_length=100, blank=True)  # Category title
    created = models.DateTimeField(default=timezone.now)  # When the category was created

    def __str__(self):  # Admin site display, easy to debug and view objects
        return self.title

    class Meta:
        db_table = 'tb_category'  # Modify table name
        verbose_name = 'Category management'
        verbose_name_plural = verbose_name


class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Author
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)  # Title image
    title = models.CharField(max_length=100, blank=True)  # title
    category = models.ForeignKey(ArticleCategory, null=True, blank=True, on_delete=models.CASCADE, related_name='artilce')  # Classification
    tags = models.CharField(max_length=20, blank=True)  # Label
    summary = models.CharField(max_length=500, null=False, blank=False)  # Summary information
    content = models.TextField()  # Article body
    total_views = models.PositiveIntegerField(default=0)  # Pageviews
    comments_count = models.PositiveIntegerField(default=0)  # Comment volume
    created = models.DateTimeField(default=timezone.now)   # Article creation time
    updated = models.DateTimeField(auto_now=True)  # The modification time of the article

    class Meta:  # Modify the table name and the configuration information displayed by the admin, etc.
        db_table = 'tb_article'
        ordering = ('-created',)
        verbose_name = 'Article management'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField()  # comments
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True)  # Commented articles
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)  # Commented user
    created = models.DateTimeField(auto_now_add=True)  # Comment time

    def __str__(self):
        return self.article.title

    class Meta:
        db_table = 'tb_comment'
        verbose_name = 'Comment management'
        verbose_name_plural = verbose_name
