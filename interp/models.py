from django.db.models.signals import post_save
from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from django.utils import timezone

from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher

from interp.utils import add_notification_to_users_cache


class User(User):
    display_name = models.CharField(max_length=255)
    language = models.ForeignKey('Language')
    country = models.ForeignKey('Country')
    font = models.CharField(max_length=255,default='')
    raw_password = models.CharField(max_length=255,default='')

    def __str__(self):
        return self.username

    def credentials(self):
        return self.language.name + '-' + self.country.name

    @staticmethod
    def get_translators():
        return User.objects.filter(is_staff=False)


class ContentVersion(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    text = models.TextField()
    create_time = models.DateTimeField(default=timezone.now())

class Task(models.Model):
    title = models.CharField(max_length=255, blank=False)
    id = models.AutoField(primary_key=True)
    is_published = models.BooleanField(default=False)
    versions = GenericRelation(ContentVersion)

    def add_version(self, text):
        return ContentVersion.objects.create(content_object=self, text=text, create_time=timezone.now())

    def get_latest_text(self):
        latest_version = self.versions.order_by('-create_time').first()
        if latest_version:
            return latest_version.text
        return ''

    def __str__(self):
        return "title : " + self.title + " id :" + str(self.id)


class Translation(models.Model):
    title = models.CharField(max_length=255, blank=False)
    user = models.ForeignKey('User')
    task = models.ForeignKey('Task', default=0)
    id = models.AutoField(primary_key=True)
    language = models.ForeignKey('Language')
    versions = GenericRelation(ContentVersion)

    def add_version(self, text):
        return ContentVersion.objects.create(content_object=self, text=text, create_time=timezone.now())

    def get_latest_text(self):
        latest_version = self.versions.order_by('-create_time').first()
        if latest_version:
            return latest_version.text
        return ''

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


# class Version(models.Model):
#     id = models.AutoField(primary_key=True)
#     translation = models.ForeignKey('Translation')
#     text = models.TextField()
#     date_time = models.DateTimeField(default=datetime.datetime.now())
#
#     def __str__(self):
#         return "id : " + str(self.id) + " Translation : " + self.translation.title

class VersionParticle(models.Model):
    id = models.AutoField(primary_key=True)
    translation = models.ForeignKey('Translation')
    text = models.TextField(default=None)
    date_time = models.DateTimeField(default=timezone.now())

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


def send_notif(sender, instance, created, *args, **kwargs):
    if created:
        add_notification_to_users_cache(User.get_translators(), instance)
        message = RedisMessage("%s^%s"%(instance.title, instance.description))
        RedisPublisher(facility='notifications', broadcast=True).publish_message(message)


post_save.connect(send_notif, sender=Notification)

class Attachment(models.Model):
    upload = models.FileField(upload_to='uploads/')
    title = models.CharField(max_length=100)
    create_time = models.DateTimeField('Date Created')


