# -*- encoding:utf-8 -*-
from django.db import models
import datetime
from django.utils import timezone


class Poll(models.Model):
    """
    Poll model, contain basic poll data.
    """
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    order = models.IntegerField(default=0)

    def __unicode__(self):
        return self.question

    def was_published_recently(self):
        """
        Check poll pub_date, return True if published recently.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date < now

    @staticmethod
    def latest_polls(number=5):
        """
        Return number latest polls.
        """
        return Poll.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:number]

    was_published_recently.admin_order_fiels = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    """
    Choice model, contain choices for polls.
    """
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __unicode__(self):
        return self.choice_text


class User(models.Model):
    """
    User model, contain anonimous user information, simple way to generate user id.
    """
    creation_time = models.DateTimeField(default=timezone.now())
    
    def save(self, *args, **kwargs):
        """
        Fill Questionnaire model with default number latest polls.
        """
        create = self.id is None
        super(User, self).save(*args, **kwargs)
        if create is not None: 
	        for poll in Poll.latest_polls():
	            Questionnaire.objects.create(user_id=self, poll=poll, choice=None)

class Questionnaire(models.Model):
    """
    Questionnaire model, contain User, Poll, Choice relationship.
    """
    user_id = models.ForeignKey(User)
    poll = models.ForeignKey(Poll)
    choice = models.ForeignKey(Choice, null=True)

