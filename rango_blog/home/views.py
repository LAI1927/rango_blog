from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from home.models import ArticleCategory, Article, Comment
from django.http.response import HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage


class IndexView(View):
    def get(self, request):
        # 1.Get all classification information
        categories = ArticleCategory.objects.all()
        # 2.The category id that received the user's click
        cat_id = request.GET.get('cat_id', 2)
        # 3.Query classification based on classification id
        try:
            category = ArticleCategory.objects.get(id=cat_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseNotFound('No such category')
        # 4.Get pagination parameters
        page_num = request.GET.get('page_num', 1)
        page_size = request.GET.get('page_size', 10)
        # 5.Query article data based on classification information
        articles = Article.objects.filter(category=category)
        # 6.Create pagination
        from django.core.paginator import Paginator, EmptyPage
        paginator = Paginator(articles, per_page=page_size)
        # 7.Pagination process
        try:
            page_articles = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')
        total_page = paginator.num_pages
        # 8.Organize the data to pass to the template
        context = {
            'categories': categories,
            'category': category,
            'articles': page_articles,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num
        }
        return render(request, 'index.html', context=context)


class DetailView(View):

    def get(self, request):
        # 1.Receive article id information
        id = request.GET.get('id')
        # 2.Query article data based on article id
        try:
            article = Article.objects.get(id=id)
        except Article.DoesNotExist:
            return render(request, '404.html')
        else:
            # Let views +1
            article.total_views += 1
            article.save()
        # 3.Query classification data
        categories = ArticleCategory.objects.all()
        # Query the top 10 article data
        hot_articles = Article.objects.order_by('-total_views')[:9]
        # 4.Get pagination request parameters
        page_size = request.GET.get('page_size', 10)
        page_num = request.GET.get('page_num', 1)
        # 5.Query comment data based on article information
        comments = Comment.objects.filter(article=article).order_by('-created')
        # Get the total number of comments
        total_count = comments.count()
        # 6.Create pagination
        paginator = Paginator(comments, page_size)
        # 7.Pagination process
        try:
            page_comments = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')
        total_page = paginator.num_pages
        context = {
            'categories': categories,
            'category': article.category,
            'article': article,
            'hot_articles': hot_articles,
            'total_count': total_count,
            'comments': page_comments,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num
        }
        return render(request, 'detail.html', context=context)

    def post(self, request):
        # 1.Receive user information first
        user = request.user
        # 2.Determine whether the user is logged in
        if user and user.is_authenticated:
            # 3.Log in users can receive form data
            # Receive comment data
            id = request.POST.get('id')
            content = request.POST.get('content')
            # Verify the existence of article
            try:
                article = Article.objects.get(id=id)
            except Article.DoesNotExist:
                return HttpResponseNotFound('There is no such article')
            # Save comment data
            Comment.objects.create(
                content=content,
                article=article,
                user=user
            )
            # Modify the number of comments on the article
            article.comments_count += 1
            article.save()
            # Refresh the current page (page redirection)
            path = reverse('home:detail')+'?id={}'.format(article.id)
            return redirect(path)
        else:
            # Users who are not logged in will be redirected to the login page
            return redirect(reverse('users:login'))
