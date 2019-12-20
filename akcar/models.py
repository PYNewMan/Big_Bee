from django.db import models

# Create your models here.
from django.db import models

class Akcar2(models.Model):

    car_id = models.CharField(max_length=20,
        verbose_name='爱卡车辆ID',unique=True)
    brand = models.CharField(max_length=200,
        verbose_name='牌子')
    car_params = models.TextField(default='',verbose_name='车辆信息')
    pic_url = models.TextField(default='',
        verbose_name='车图url')
    score_kb = models.TextField(default='',
                                verbose_name='爱卡用户评分')
    series = models.CharField(
        max_length=200,verbose_name='车型系列'
    )
    class Meta:
        db_table = 'Akcar2'

    def __str__(self):
        return 'car_id:%s brand:%s series:%s score_kb:%s'%(self.car_id,self.brand,self.series,self.score_kb)




