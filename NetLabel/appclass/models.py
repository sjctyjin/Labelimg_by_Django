from django.db import models

import time
# Create your models here.
class Article(models.Model):
    
    thunmbnial = models.FileField(upload_to=f'static/%Y%m%D%S')
       