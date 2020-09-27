from django.db import models

# Create your models here.
'''
class personal_info(models.Model):
    enroll = models.CharField(max_length=12)
    email = models.CharField(max_length=70)
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    branch = models.CharField(max_length=4)
    batch = models.IntegerField()
    gender = models.CharField(max_length=8)
    passwd = models.CharField(max_length=256)
'''
class profileimage(models.Model):
    profile_Image = models.ImageField(upload_to='images/')




