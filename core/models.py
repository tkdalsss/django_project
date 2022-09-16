from django.db import models
from . import managers

# Create your models here.
class TimeStampedModel(models.Model):
    
    """ Time Stamped Model """

    created = models.DateTimeField(auto_now_add=True)  # auto_now_add -> 모델이 생성된 날짜
    updated = models.DateTimeField(auto_now=True)  # auto_now -> 모델을 업데이트 할 때마다 바꿔줌 
    objects = managers.CustomReservationmanager()

    class Meta:
        abstract = True
