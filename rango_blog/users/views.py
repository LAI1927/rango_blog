from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponseBadRequest, HttpResponse
from django.http.response import JsonResponse
from django_redis import get_redis_connection
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError
from django.urls import reverse
from utils.response_code import RETCODE
from libs.yuntongxun.sms import CCP
from libs.captcha.captcha import captcha
from home.models import ArticleCategory, Article
from users.models import User
from random import randint
import re
import logging
logger = logging.getLogger('django')


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 1. Receive data
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        smscode = request.POST.get('sms_code')
        # 2.verify the data
        # If the parameters complete
        if not all([mobile, password, password2, smscode]):
            return HttpResponseBadRequest('Missing required parameters')
        # Is the format of the phone number correct?
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('Mobile phone number does not meet the rules')
        # Whether the password conforms to the format
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest('Please enter 8-20 digits password, the password is numbers and letters')
        # Password and confirm password must be the same
        if password != password2:
            return HttpResponseBadRequest('The two passwords are inconsistent')
        # Is the SMS verification code the same as that in redis
        redis_conn = get_redis_connection('default')
        redis_sms_code = redis_conn.get('sms:%s' % mobile)
        if redis_sms_code is None:
            return HttpResponseBadRequest('SMS verification code has expired')
        if smscode != redis_sms_code.decode():
            return HttpResponseBadRequest('Inconsistent SMS verification codes')
        # 3.Save registration information
        try:
            user = User.objects.create_user(username=mobile,
                                            mobile=mobile,
                                            password=password)
        except DatabaseError as e:
            logger.error(e)
            return HttpResponseBadRequest('registration failed')
        from django.contrib.auth import login
        login(request, user)
        # 4.Return the response and jump to the specified page
        response = redirect(reverse('home:index'))
        # Set cookie information to facilitate the judgment of user information display on the homepage and the display of user information
        response.set_cookie('is_login', True)
        response.set_cookie('username', user.username, max_age=7 * 24 * 3600)

        return response


class ImageCodeView(View):
    def get(self, request):
        uuid = request.GET.get('uuid')
        # Determine whether the parameter is None
        if uuid is None:
            return HttpResponseBadRequest('Request parameter error')
        # Obtain verification code content and verification code image binary data
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('default')
        redis_conn.setex('img:%s' % uuid, 300, text)
        # Return the response, and return the generated image to the request in the form of content_type as image/jpeg
        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):
    def get(self, request):
        # 1.Receive parameters (passed in the form of query string)
        mobile = request.GET.get('mobile')
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # 2.Verification of parameters
        # Verify that the parameters are complete
        if not all([mobile, image_code, uuid]):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': 'Missing required parameters'})
        # Image verification code verification
        # Connect to redis to get the image verification code in redis
        redis_conn = get_redis_connection('default')
        redis_image_code = redis_conn.get('img:%s'%uuid)
        # Determine whether the image verification code exists
        if redis_image_code is None:
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'Image verification code has expired'})
        # If the image verification code has not expired, we can delete the image verification code after we obtain it
        try:
            redis_conn.delete('img:%s'%uuid)
        except Exception as e:
            logger.error(e)
        # Compare the image verification code, pay attention to the case, redis data is of type bytes
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'Image verification code error'})
        # 3.Generate SMS verification code
        sms_code = '%06d'%randint(0, 999999)
        logger.info(sms_code)
        # 4.Save the SMS verification code to redis
        redis_conn.setex('sms:%s'%mobile, 300, sms_code)
        # 5.send messages
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # 6.Return response
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'SMS sent successfully'})


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 1.Receive parameters
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        # 2.Verification of parameters
        # Verify that the phone number complies with the rules
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('Mobile phone number does not meet the rules')
        # Verify that the password complies with the rules
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return HttpResponseBadRequest('Password does not meet the rules')
        # 3.User authentication login
        from django.contrib.auth import authenticate
        user = authenticate(mobile=mobile, password=password)
        if user is None:
            return HttpResponseBadRequest('用户名或密码错误')
        # 4.State maintenance
        from django.contrib.auth import login
        login(request, user)
        # 5.Judge according to whether the user chooses to remember the login status
        # 6.In order to display on the homepage we need to set some cookie information
        next_page = request.GET.get('next')
        if next_page:
            response = redirect(next_page)
        else:
            response = redirect(reverse('home:index'))

        if remember != 'on':
            request.session.set_expiry(0)
            response.set_cookie('is_login', True)
            response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        else:  # Remember user information
            request.session.set_expiry(None)
            response.set_cookie('is_login', True, max_age=14 * 24 * 3600)
            response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        # 7.Return response
        return response


class LogoutView(View):

    def get(self, request):
        # 1.session data clear
        logout(request)
        # 2.Delete some cookie data
        response = redirect(reverse('home:index'))
        response.delete_cookie('is_login')
        # 3.Jump to homepage
        return response


class ForgetPasswordView(View):

    def get(self, request):
        return render(request, 'forget_password.html')

    def post(self, request):
        # 1.Receive data
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        smscode = request.POST.get('sms_code')
        # 2.verify the data
        if not all([mobile, password, password2, smscode]):
            return HttpResponseBadRequest('Incomplete parameters')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('Mobile phone number does not meet the criteria')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest('Password does not meet the rules')
        if password2 != password:
            return HttpResponseBadRequest('Inconsistent passwords')
        redis_conn = get_redis_connection('default')
        redis_sms_code = redis_conn.get('sms:%s' % mobile)
        if redis_sms_code is None:
            return HttpResponseBadRequest('SMS verification code has expired')
        if redis_sms_code.decode() != smscode:
            return HttpResponseBadRequest('SMS verification code error')
        # 3.Query user information based on mobile phone number
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 5.If the mobile phone number does not find out the user information, create a new user
            try:
                User.objects.create_user(username=mobile,
                                         mobile=mobile,
                                         password=password)
            except Exception:
                return HttpResponseBadRequest('修改失败，请稍后再试')
        else:
            user.set_password(password)
            user.save()
        # 6.Jump to the page, jump to the login page
        response = redirect(reverse('users:login'))
        # 7.Return response
        return response


class UserCenterView(LoginRequiredMixin, View):
    def get(self, request):
        # 获得登录用户的信息
        user = request.user
        # 组织获取用户的信息
        context = {
            'username': user.username,
            'mobile': user.mobile,
            'avatar': user.avatar.url if user.avatar else None,
            'user_desc': user.user_desc
        }
        return render(request, 'center.html', context=context)

    def post(self, request):
        user = request.user
        # 1.Receive parameters
        username = request.POST.get('username', user.username)
        user_desc = request.POST.get('desc', user.user_desc)
        avatar = request.FILES.get('avatar')
        # 2.Save the parameters
        try:
            user.username = username
            user.user_desc = user_desc
            if avatar:
                user.avatar = avatar
            user.save()
        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest('Edit failed, please try again later')
        # 3.Update the username information in the cookie
        # 4.Refresh the current page (redirect operation)
        response = redirect(reverse('users:center'))
        response.set_cookie('username', user.username, max_age=14 * 3600 * 24)
        # 5.Return response
        return response


class WriteBlogView(LoginRequiredMixin, View):
    def get(self, request):
        categories = ArticleCategory.objects.all()  # Query all classification models
        context = {
            'categories': categories
        }
        return render(request, 'write_blog.html', context=context)

    def post(self, request):
        # 1.Receive data
        avatar = request.FILES.get('avatar')
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        tags = request.POST.get('tags')
        summary = request.POST.get('summary')
        content = request.POST.get('content')
        user = request.user
        # 2.verify the data
        if not all([avatar, title, category_id, summary, content]):
            return HttpResponseBadRequest('Incomplete parameters')
        try:
            category = ArticleCategory.objects.get(id=category_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseBadRequest('No such category')
        # 3.Data storage
        try:
            article = Article.objects.create(
                author=user,
                avatar=avatar,
                title=title,
                category=category,
                tags=tags,
                summary=summary,
                content=content
            )
        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest('Publish failed, please try again later')
        # 4.Jump to the specified page (temporary home page)
        return redirect(reverse('home:index'))
