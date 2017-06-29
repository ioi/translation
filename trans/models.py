import datetime

from django.db.models.signals import post_save, post_delete
from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from django.utils import timezone

from trans.utils import add_notification_to_users_cache, remove_notification


class User(User):
    language = models.ForeignKey('Language')
    country = models.ForeignKey('Country')
    raw_password = models.CharField(max_length=255, default='')
    text_font_base64 = models.TextField(default='', blank=True)
    text_font_name = models.CharField(max_length=255, default='', blank=True)

    def __str__(self):
        return self.username

    def credentials(self):
        return self.country.name + '_' + self.language.name

    @staticmethod
    def get_translators():
        return User.objects.filter(is_staff=False)

    def is_editor(self):
        return self.groups.filter(name="editor").exists() or self.is_superuser

class ContentVersion(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    text = models.TextField()
    released = models.BooleanField(default=False)
    release_note = models.CharField(max_length=255, blank=True)
    create_time = models.DateTimeField(default=timezone.now)

    def can_view_by(self, user):
        if self.content_type.model == 'translation' and self.content_object.user != user:
            return False
        return True


class Contest(models.Model):
    title = models.CharField(max_length=100, blank=False)
    order = models.IntegerField()
    slug = models.CharField(max_length=10, blank=False, unique=True)
    public = models.BooleanField(default=False)

    def __str__(self):
        return "{} (order: {})".format(self.title, self.order)


class Task(models.Model):
    name = models.CharField(max_length=255, blank=False)
    contest = models.ForeignKey('Contest', default=None)
    frozen = models.BooleanField(default=False)
    versions = GenericRelation(ContentVersion)

    def add_version(self, text, release_note="", released=False):
        return ContentVersion.objects.create(content_object=self, text=text, create_time=timezone.now(),
                                             release_note=release_note, released=released)

    def get_corresponding_translation(self):
        return Translation.objects.filter(user__username='ISC', task=self).first()

    def publish_latest(self, release_note):
        ISC_translation = self.get_corresponding_translation()
        if not ISC_translation:
            return None
        latest_version = ISC_translation.versions.order_by('-create_time').first()
        if not latest_version:
            return None
        query_set = ISC_translation.versions.filter(id=latest_version.id)
        return query_set.update(release_note=release_note, released=True, create_time=timezone.now())

    def get_latest_text(self):
        ISC_translation = self.get_corresponding_translation()
        if ISC_translation:
            return ISC_translation.get_latest_text()
        return ""

    def get_published_text(self):
        ISC_translation = self.get_corresponding_translation()
        if ISC_translation:
            return ISC_translation.get_published_text()
        return ""

    def is_published(self):
        ISC_translation = self.get_corresponding_translation()
        if ISC_translation:
            return ISC_translation.versions.filter(released=True).exists()
        return False

    def get_latest_change_time(self):
        ISC_translation = self.get_corresponding_translation()
        latest_published_version = ISC_translation.versions.filter(released=True).order_by('-create_time').first()
        if latest_published_version:
            return latest_published_version.create_time
        return None

    def __str__(self):
        return "name : " + str(self.name) + " id :" + str(self.id)


class Translation(models.Model):
    user = models.ForeignKey('User')
    task = models.ForeignKey('Task', default=0)
    frozen = models.BooleanField(default=False)
    versions = GenericRelation(ContentVersion)

    def add_version(self, text, release_note=""):
        return ContentVersion.objects.create(content_object=self, text=text, release_note=release_note, create_time=timezone.now())

    def get_latest_text(self):
        latest_version = self.versions.order_by('-create_time').first()
        latest_version_particle = self.versionparticle_set.order_by('-create_time').first()
        if latest_version_particle:
            if not latest_version or latest_version_particle.create_time > latest_version.create_time:
                return latest_version_particle.text
        if latest_version:
            return latest_version.text
        return ''

    def get_published_text(self):
        latest_published_version = self.versions.filter(released=True).order_by('-create_time').first()
        if latest_published_version:
            return latest_published_version.text
        return None

    def get_latest_change_time(self):
        latest_version = self.versions.order_by('-create_time').first()
        latest_version_particle = self.versionparticle_set.order_by('-create_time').first()
        if latest_version_particle:
            return latest_version_particle.create_time
        if latest_version:
            if latest_version_particle and latest_version_particle.create_time > latest_version.create_time:
                return latest_version_particle.create_time
            return latest_version.create_time
        return None

    def __str__(self):
        return "{} ({})".format(self.task.name, self.user.username)


class Language(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    code = models.CharField(unique=True, max_length=255, default='')
    rtl = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=255,primary_key=True)
    code = models.CharField(unique=True, max_length=255,default='')

    def __str__(self):
        return self.name


class VersionParticle(models.Model):
    translation = models.ForeignKey('Translation')
    text = models.TextField(default=None)
    create_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{}: {} ({})".format(self.id, self.translation.task.name, self.translation.user.username)


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
    create_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "%s-%s" % (self.title, self.description)


def send_notif(sender, instance, created, *args, **kwargs):
    if created:
        add_notification_to_users_cache(User.objects.all(), instance)
        # Redis Messages
        # message = RedisMessage("%s^%s"%(instance.title, instance.description))
        # RedisPublisher(facility='notifications', broadcast=True).publish_message(message)


def remove_notif(sender, instance, *args, **kwargs):
    remove_notification(User.objects.all(), instance)


post_save.connect(send_notif, sender=Notification)
post_delete.connect(remove_notif, sender=Notification)


class Attachment(models.Model):
    uploaded_file = models.FileField(upload_to='uploads/')
    title = models.CharField(max_length=100)
    create_time = models.DateTimeField('Date Created')

    def __str__(self):
        return self.title


class FlatPage(models.Model):
    slug = models.CharField(max_length=100, primary_key=True)
    content = models.TextField(default=None, blank=True)

    def __str__(self):
        return self.slug
