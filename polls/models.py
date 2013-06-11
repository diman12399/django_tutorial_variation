# -*- encoding:utf-8 -*-
from django.db import models


class Pool(models.Model):
    question = models.CharField(max_length=200)
    pun_date = models.DateTimeField('date published')


class Chice(models.Model):
    pool = models.ForeignKey(Pool)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

