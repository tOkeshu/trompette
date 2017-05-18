from enum import Enum
import re

from django.db.models import Model, CharField, TextField, DateTimeField, IntegerField, CASCADE
from django.db.models import ForeignKey, OneToOneField, ManyToManyField
from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.utils.timezone import now

class Account(Model):

    user      = OneToOneField(User, on_delete=CASCADE)
    username  = CharField(max_length=100)
    following = ManyToManyField('self', symmetrical=False, related_name='followed_by')


class Tag(Model):

    name = CharField(max_length=500, unique=True)


class Status(Model):

    content     = TextField(max_length=500)
    account     = ForeignKey(Account, related_name='statuses')
    boosts      = ManyToManyField(Account, related_name='boosts', through='Boost')
    created_at  = DateTimeField(auto_now_add=True)
    in_reply_to = ForeignKey('self', related_name='replies', null=True)
    thread      = ForeignKey('self', related_name='+', null=True)
    tags        = ManyToManyField(Tag, related_name='statuses')


class Boost(Model):

    account = ForeignKey(Account)
    status  = ForeignKey(Status)
    at      = DateTimeField()


Notif = Enum("Notif", "mention follow")

class Notification(Model):

    account = ForeignKey(Account, related_name='notifications')

    mention = ForeignKey(Status,  related_name='+', null=True)
    # fave  = ForeignKey(Account, related_name='+')
    follow  = ForeignKey(Account, related_name='+', null=True)
    at      = DateTimeField()
    _type   = IntegerField(choices=((n.value, n.name) for n in Notif))

    @property
    def type(self):
        return Notif(self._type).name


###########
# Signals #
###########

@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance, username=instance.username)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.account.save()

@receiver(post_save, sender=Status)
def attach_to_thread(sender, instance, created, **kwargs):
    if not created:
        return

    status = instance
    # Attach the status to the current thread
    # If it is a brand new status, create a new thread
    if status.in_reply_to:
        status.thread  = status.in_reply_to.thread
        status.save()
    else:
        status.thread_id = status.id
        status.save()

def get_hashtag(name):
    try:
        tag = Tag.objects.get(name=name)
    except Tag.DoesNotExist:
        tag = Tag(name=name)
        tag.save()
    return tag

@receiver(post_save, sender=Status)
def attach_to_hashtags(sender, instance, created, **kwargs):
    if not created:
        return

    status = instance
    # Find hashtags and tie the status to them
    for name in re.findall('#(\w+)', status.content):
        tag = get_hashtag(name)
        status.tags.add(tag)
    status.save()

@receiver(post_save, sender=Status)
def notify_mentioned_users(sender, instance, created, **kwargs):
    if not created:
        return

    status = instance
    # Find mentions and notify the corresponding users
    for handle in re.findall('@(\w+)', status.content):
        try:
            account = Account.objects.get(username=handle)
            if status.account == account:
                continue

            notification = Notification(
                account=account,
                _type=Notif.mention.value,
                mention=status,
                at=status.created_at
            )
            notification.save()
        except Account.DoesNotExist:
            pass

@receiver(m2m_changed, sender=Account.following.through)
def notify_followed_users(sender, instance, action, **kwargs):
    if action not in ["post_add", "post_remove"]:
        return

    account = instance
    if action == "post_add":
        follows = kwargs["pk_set"]
        for pk in follows:
            target = Account.objects.get(pk=pk)
            notification = Notification(
                account=target,
                _type=Notif.follow.value,
                follow=account,
                at=now()
            )
            notification.save()

    if action == "post_remove":
        unfollows = kwargs["pk_set"]
        for pk in unfollows:
            target = Account.objects.get(pk=pk)
            query = Notification.objects.filter(account=target, follow=account)
            for notification in query:
                notification.delete()

