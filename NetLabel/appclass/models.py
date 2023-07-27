from django.db import models
from django.contrib.auth.models import User

import time
import datetime
# Create your models here.
class Articles(models.Model):

    thunmbnial = models.FileField(upload_to=f'static/%Y%m%D%S')

class Training_cycle(models.Model):
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    progress = models.CharField(max_length=100)
    finish_time = models.DateTimeField(default=datetime.datetime.now(), verbose_name='時間')

    # def __str__(self):
    #     return f"{self.userid.username} - {self.my_string}"