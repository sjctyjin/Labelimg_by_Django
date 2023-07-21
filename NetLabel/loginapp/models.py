import datetime

from django.db import models

# Create your models here.

class Test(models.Model):
    name = models.CharField(max_length=20,verbose_name='用戶名')
    age = models.IntegerField(default=0,verbose_name='年齡')
    info = models.TextField(verbose_name='個人訊息')
    sex = models.CharField(choices=(('Male','男'),('Female','女')),max_length=6,default='Male',verbose_name='性別')
    create_time = models.DateTimeField(default=datetime.datetime.now(),verbose_name='時間')
    def __str__(self):
        return 'name : {}'.format(self.name)
    class Meta:
        verbose_name = '用戶表'
        verbose_name_plural = verbose_name
class Apage(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return 'title:{}'.format(self.title)
    class Meta:
        permissions = [
            ('look_a_page','can get this page message')
        ]

class Bpage(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return 'title:{}'.format(self.title)
    class Meta:
        permissions = [
            ('look_b_page','can get this page message')
        ]