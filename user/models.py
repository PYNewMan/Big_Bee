from django.db import models

# Create your models here.
from django.db import models

class UserProfile(models.Model):

    customer = models.CharField(max_length=11,
        verbose_name='用户名称',unique=True)
    password = models.CharField(max_length=32,
        verbose_name='密码')
    email = models.EmailField(default='')
    isActive = models.BooleanField(default=False,
        verbose_name='是否激活')
    create_time = models.DateTimeField(
        auto_now_add=True
    )
    # 修改时间
    update_time = models.DateTimeField(
        auto_now=True
    )
    phone = models.CharField(max_length=11,verbose_name='手机号',default='')

    class Meta:
        db_table = 'user_profile'

    def __str__(self):
        return 'id:%s customer:%s'%(self.id,self.customer)


class WeiboUser(models.Model):

    # 微博用户表
    uid = models.OneToOneField(UserProfile,null=True)
    wuid = models.CharField(max_length=50,db_index=True,verbose_name='微博用户id')
    access_token = models.CharField(max_length=100,verbose_name='授权令牌')

    class Meta:
        db_table = 'weibo_user'

    def __str__(self):
        return "%s_%s"%(self.wuid,self.uid)





