import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rango_blog.settings')

import os
import pathlib
import random
import sys
import faker
from datetime import timedelta
from django.utils import timezone

import django
django.setup()
from users.models import User
from home.models import Article, ArticleCategory, Comment

back = os.path.dirname
BASE_DIR = back(back(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


def populate():
    print("clean database")
    User.objects.all().delete()
    Article.objects.all().delete()
    ArticleCategory.objects.all().delete()
    Comment.objects.all().delete()

    user = [
        {'id' : 1,
         'username' : "admin",
         'mobile' : 13914782478,
         'password' : '12345678'
        },
        {'id' : 2,
         'username' : "gla",
         'mobile' : 13911111111,
         'password' : '12345678'      
        },
    ]

    print("create a blog user")
    for u in user:
        creat_use = User.objects.create(id=u['id'],username=u['username'],mobile=u['mobile'],password=['password']) 
    # user1 = User.objects.create(id=1,username="admin",mobile=12300000000,password='12345678')
    # user2 = User.objects.create(id=2,username='gla',mobile=12340000000,password='12345678')

    category_list = ["Python", "Java","C++"]

    print("create categories and tags")
    i=0
    for cate in category_list:
        i=i+1
        ArticleCategory.objects.create(title=cate,id=i)

    print("create article")
    fake = faker.Faker()
    i=0
    for _ in range(10):
        i=i+1
        Article.objects.create(id=i,title='Python_test',avatar='article/20210805/IMG_0069.JPG',tags="Test",summary="This is for test",
                            content="\n\n".join(fake.paragraphs(10)),author_id=1,category_id=1,total_views=20,comments_count=5)

    i=10
    for _ in range(10):
        i=i+1
        Article.objects.create(id=i,title='Java_test',avatar='article/20210805/IMG_0060_UNXwcCM.JPG',tags="Test",summary="This is for test",
                            content="\n\n".join(fake.paragraphs(10)),author_id=1,category_id=2,total_views=20,comments_count=5)

    i=20
    for _ in range(10):
        i=i+1
        Article.objects.create(id=i,title='C++_test',avatar='article/20210805/IMG_0060_UNXwcCM.JPG',tags="Test",summary="This is for test",
                            content="\n\n".join(fake.paragraphs(10)),author_id=1,category_id=3,total_views=20,comments_count=5)

    print("create some comments")
    for article in Article.objects.all():
        for _ in range(random.randrange(3, 8)):
            Comment.objects.create(
               content='good',
               article_id = article.id,
               user_id = 2, 
            )

    print("done!")


# Start here!
if __name__ == '__main__':
    print('Starting Rango_blog population script...')
    populate()
