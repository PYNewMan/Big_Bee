import base64
import json
import random
from urllib.parse import urlencode

import requests

from akcar.models import Akcar2
from .tasks import send_active_email
from veh_eng import settings
from django.db import transaction
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render

# Create your views here.
from django.views import View

from che_token.views import make_token
from user.models import UserProfile, WeiboUser

import redis
r = redis.Redis(host='127.0.0.1',port=6379,db=1)

class Users(View):

    def get(self,request):

        return JsonResponse({'code':200})

    def post(self,request):

        data = request.body
        if not data:
            result = {'code': '10101',
                      'error': 'Please give me data'}
            return JsonResponse(result)

        json_obj = json.loads(data)
        customer = json_obj.get('uname')
        email = json_obj.get('email')
        phone = json_obj.get('phone')
        password = json_obj.get('password')

        # 检查用户名是否可用

        old_user = UserProfile.objects.filter(
            customer=customer
        )
        if old_user:
            result = {'code': '10102',
                      'error': {'message': 'The customer is existed !'}}
            return JsonResponse(result)

        # 生成密码哈希
        import hashlib
        m = hashlib.md5()
        m.update(password.encode())
        # 创建用户
        try:
            print(customer,email,phone,m.hexdigest())
            user = UserProfile.objects.create(
                customer=customer, email=email, phone=phone,
                password=m.hexdigest())
        except Exception as e:
            result = {'code': '10103', 'error': {'message': 'The customer is existed !'}}
            return JsonResponse(result)
        # 生成token
        token = make_token(customer)

        # 签发token
        # {‘code’:200,'data':({'token':xxxxx})}

        # TODO 发激活邮件
        random_int = random.randint(1000, 9999)
        code_str = customer + '_' + str(random_int)
        code_str_bs = base64.urlsafe_b64encode(code_str.encode())
        # 将随机码组合 存储到redis中 可以扩展成存储1-3天
        r.set('email_active_%s' % (customer), code_str)
        active_url = 'http://127.0.0.1:7002/veh_eng/templates/active.html?code=%s' % (code_str_bs.decode())

        # 发邮件
        # celery异步执行
        send_active_email(email, active_url)

        return JsonResponse({'code': 200, 'customer': customer, 'data': {
            'token': token.decode()
        }})

    def delete(self, request):
        pass

def users_active(request):


    # 激活用户
    if request.method != 'GET':
        result = {'code':10104,'error':{'message':'Please use GET !!'}}
        return JsonResponse(result)

    code = request.GET.get('code')
    if not code:
        pass
    # 解析code
    try:
        code_str = base64.urlsafe_b64decode(code.encode())
        # customer_9999
        new_code_str = code_str.decode()
        customer,rcode = new_code_str.split('_')
    except Exception as e:
        result = {'code':10105,'error':{'message':'You code is worng !'}}
        return JsonResponse(result)

    old_data = r.get('email_active_%s'%(customer))
    if not old_data:
        result = {'code':10106,'error':{
            'message':"Your code is wrong! "
        }}
        return JsonResponse(result)

    if code_str != old_data:
        result = {'code':10107,'error':{
            'message':'Your code is wrong!'
        }}
        return JsonResponse(result)

    # 激活用户
    users = UserProfile.objects.filter(
        customer = customer
    )
    if not users:
        pass
    user = users[0]
    user.isActive = True
    user.save()

    # 删除redis数据
    r.delete('email_active_%s'%(customer))
    result = {'code':200,'data':{'message':'激活成功'}}
    return JsonResponse(result)



class OAuthWeiboUrlView(View):

    def get(self,request):
        # 获取登录地址
        url = get_weibo_login_url()
        return JsonResponse({'code':200,
                'oauth_url':url})

def get_weibo_login_url():
    # response_type - code 代表启用授权码模式
    # scope 授权范围
    params = {'response_type':'code',
              'client_id':settings.WEIBO_CLIENT_ID,
              'redirect_uri':settings.WEIBO_REDIRECT_URI,
              'scope':''}
    weibo_url = 'https://api.weibo.com/oauth2/authorize?'
    url = weibo_url + urlencode(params)

    return url

class OAuthWeiboView(View):

    def get(self,request):
        # 获取前端传来的 微博code
        code = request.GET.get('code')
        # 向微博服务器发送请求  用户code换取token
        # websocket
        try:
            user_info = get_access_token(code)
        except Exception as e:
            print('---get_access_token error')
            print(e)
            result = {'code':202,'error':
                {'message':'Weibo server is busy ~'}}
            return JsonResponse(result)
        """
        {'access_token': '2.006QZ45DlMMViD7653cf2deaM2PNTC',
         'remind_in': '157679999', 'expires_in': 157679999, 
         'uid': '3108647661', 'isRealName': 'true'}
        """
        # 微博用户id
        wuid = user_info.get('uid')
        access_token = user_info.get('access_token')

        #查询weibo用户表，判断是否第一次光临
        try:
            list1 = Akcar2.objects.all()
            print(list1)
            weibo_user = WeiboUser.objects.get(wuid=wuid)
        except Exception as e:
            print('weibouser get error')
            # 该用户第一次用微博登录
            # 创建数据 & 暂时不绑定UserProfile
            WeiboUser.objects.create(
                access_token=access_token,wuid=wuid
            )
            data = {'code':"201",'uid':wuid}
            return JsonResponse(data)
        else:
            # 该用户非第一次微博登录
            # 检查是否进行过绑定
            uid = weibo_user.uid
            if uid:
                # 之前绑定过，则认为当前为正常登录，签发token
                username = uid.customer
                token = make_token(username)
                result = {'code':200,
                          'username':username,'data':{
                          'token':token.decode()
                    }}
                return JsonResponse(result)
            else:
                # 之前微博登录过，但是没有执行微博绑定注册
                data = {'code':'201','uid':wuid}
                return JsonResponse(data)

    def post(self,request):
        # 绑定注册
        # 前端将weiboid 命名为uid POST过来
        # 返回值 跟正常注册是一样
        data = json.loads(request.body)
        # 获取微博的用户id
        uid = data.get('uid')
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')
        #TODO 检查参数 是否存在
        import hashlib
        m = hashlib.md5()
        m.update(password.encode())
        password_m = m.hexdigest()

        try:
            # 注册用户  事务
            with transaction.atomic():
                user = UserProfile.objects.create(customer=username,phone=phone,email=email,password=password_m)
                weibo_user = WeiboUser.objects.get(wuid = uid)
                weibo_user.uid = user
                weibo_user.save()

        except Exception as e:
            print('---weibo register error---')
            print(e)
            return JsonResponse({'code':10115,
            'error':{'message':'The username is existed !'}})
        # 签发token
         # TODO 发邮件
        token = make_token(username)
        result = {'code':200,'username':username,'data':{'token':token.decode()}}
        return JsonResponse(result)


def get_access_token(code):

    # 向资源授权平台 换区token
    token_url = 'https://api.weibo.com/oauth2/access_token'
    post_data = {
        'client_id':settings.WEIBO_CLIENT_ID,
        'client_secret':settings.WEIBO_CLIENT_SECRET,
        'grant_type':'authorization_code',
        'redirect_uri':settings.WEIBO_REDIRECT_URI,
        'code':code
    }

    try:
        # 向微博服务器发送请求
        res = requests.post(token_url, data=post_data)
        print(res,res.text,'88888')
    except Exception as e:
        print('--weibo request error --')
        print(e)
        raise
    if res.status_code == 200:
        # res.text 就是response的返回
        return json.loads(res.text)






