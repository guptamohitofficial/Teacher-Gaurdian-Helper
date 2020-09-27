from django.db import models

# Create your models here.

class admin_auth(models.Model):
    username = models.CharField(max_length=12)
    name = models.CharField(max_length=70)
    email = models.EmailField(max_length=60)
    password = models.CharField(max_length=260)

class allot_tg(models.Model):
    tg_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    have_class = models.CharField(max_length=15,primary_key=True) 
    tg_email = models.EmailField(max_length=60)
    password =  models.CharField(max_length=260)
    description = models.CharField(max_length=1000)

class semister(models.Model):
    sem = models.IntegerField()
    class_name = models.CharField(max_length=15)
    subjects = models.CharField(max_length=150)

