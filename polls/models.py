# -*- encoding:utf-8 -*-
from django.db import models


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pun_date = models.DateTimeField('date published')


class Chice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

