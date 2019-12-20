import json
import time

# Create your views here.
from django.http import JsonResponse

# Create your views here.
from user.models import UserProfile



def tokens(request):

    #登录
    if not request.method == 'POST':
        result = {'code':'10201','error':'Please use POST'}
        return JsonResponse(result)

    data = request.body
    json_obj = json.loads(data)
    customer = json_obj.get('username')
    password = json_obj.get('password')

    # TODO 检查参数是否存在

    # 查询用户
    user = UserProfile.objects.filter(customer=customer)

    if not user:
        result = {'code':10202,'error':'customer or password is wrong'}
        return JsonResponse(result)

    user = user[0]
    import hashlib
    m = hashlib.md5()
    m.update(password.encode())
    if m.hexdigest() != user.password:
        result = {'code':10203,'error':'customer or password is wrong'}
        return JsonResponse(result)
    # 生成token
    token = make_token(customer)
    result = {'code':'200','customer':customer,'data':{'token':token.decode()}}
    return JsonResponse(result)


def make_token(customer,expire=3600*24):
    # 注册/登录成功后 签发token 默认一天有效期
    import jwt
    from django.conf import settings
    key = settings.JWT_TOKEN_KEY
    now = time.time()
    payload = {'customer':customer,'exp':now+expire}
    return jwt.encode(payload,key,algorithm='HS256')



