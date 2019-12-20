from django.db import models

# Create your models here.
from django.db import models

class Article(models.Model):

    title = models.CharField(max_length=30,
        verbose_name='文章题目')
    author = models.CharField(max_length=20,
        verbose_name='作者')
    content = models.TextField(default='',
        verbose_name='文章内容')

    class Meta:
        db_table = 'Article'

    def __str__(self):
        return 'id:%s title:%s author:%s'%(self.id,self.title,self.author)


