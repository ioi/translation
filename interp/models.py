from django.db.models.signals import post_save
from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models
import datetime

from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher


class User(User):
    display_name = models.CharField(max_length=255)
    rtl = models.BooleanField(default=False)
    language = models.ForeignKey('Language')
    country = models.ForeignKey('Country')
    font = models.CharField(max_length=255,default='')
    raw_password = models.CharField(max_length=255)
    def __str__(self):
        return self.username


class Task(models.Model):
    title = models.CharField(max_length=255, blank=False)
    id = models.AutoField(primary_key=True)
    text = models.TextField()
    is_published = models.BooleanField(default=False)
    def __str__(self):
        return "title : " + self.title + " id :" + str(self.id)


class Translation(models.Model):
    title = models.CharField(max_length=255, blank=False)
    user = models.ForeignKey('User')
    task = models.ForeignKey('Task', default=0)
    text = models.TextField()
    id = models.AutoField(primary_key=True)
    language = models.ForeignKey('Language')

    def __str__(self):
        return "Title : "+ self.title + " id : " + str(self.id)


class Language(models.Model):
    name = models.CharField(max_length=255,primary_key=True)
    abbreviation = models.CharField(max_length=255,default='')
    rtl = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=255,primary_key=True)
    abbreviation = models.CharField(max_length=255,default='')
    def __str__(self):
        return self.name

class Version(models.Model):
    id = models.AutoField(primary_key=True)
    translation = models.ForeignKey('Translation')
    text = models.TextField()
    date_time = models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return "id : " + str(self.id) + " Translation : " + self.translation.title

class VersionParticle(models.Model):
    id = models.AutoField(primary_key=True)
    translation = models.ForeignKey('Translation')
    text = models.TextField(default=None)
    date_time = models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return "id : " + str(self.id) + " Translation : " + self.translation.title


# Uncomment here when wanted to email people

# def email_new_user(sender, **kwargs):
#     if kwargs["created"]:  # only for new users
#         new_user = kwargs["instance"]
#         print(new_user.email)
#         email = EmailMessage('Hello', 'World', to=[new_user.email])
#         email.send()
#
# post_save.connect(email_new_user, sender=User)

class Notification(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    pub_date = models.DateTimeField('date published')


def send_notif(sender, instance, *args, **kwargs):
    message = RedisMessage("%s^%s"%(instance.title, instance.description))
    RedisPublisher(facility='notifications', broadcast=True).publish_message(message)


post_save.connect(send_notif, sender=Notification)

class Attachment(models.Model):
    upload = models.FileField(upload_to='uploads/')
    title = models.CharField(max_length=100)
    create_time = models.DateTimeField('Date Created')


