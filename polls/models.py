# -*- encoding:utf-8 -*-
from django.db import models
import datetime
from django.utils import timezone


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    order = models.IntegerField(default=0)

    def __unicode__(self):
        return self.question

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date < now

    @staticmethod
    def latest_polls():
        return Poll.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

    was_published_recently.admin_order_fiels = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __unicode__(self):
        return self.choice_text


class User(models.Model):
    creation_time = models.DateTimeField(default=timezone.now())
    
    def save(self, *args, **kwargs):
        create = self.id is None
        super(User, self).save(*args, **kwargs)
        if create: 
	    for poll in Poll.latest_polls():
	        Questionnaire.objects.create(user_id=self, poll=poll, choice=None)

class Questionnaire(models.Model):
    user_id = models.ForeignKey(User)
    poll = models.ForeignKey(Poll)
    choice = models.ForeignKey(Choice, null=True)

