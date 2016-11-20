from django.db import models
from django.contrib.auth.models import User

class User(User):
    display_name = models.CharField(max_length=255)
    rtl = models.BooleanField(default=False)

class Origques(models.Model):
    title = models.CharField(max_length=255, blank=False)
    id = models.AutoField(primary_key=True)
    text = models.TextField()


    def __str__(self):
        return self.title + " id :" + str(self.id)


class Question(models.Model):
    title = models.CharField(max_length=255, blank=False)
    user = models.ForeignKey('User')
    origques = models.ForeignKey('Origques', default=0)
    text = models.TextField()
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return self.title + str(self.id)

class History(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey('Question')

