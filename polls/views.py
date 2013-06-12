# -*- encoding:utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from polls.models import Poll

def index(request):
    latest_polls_list = Poll.objects.order_by('-pub_date')[:5]
    context = {'latest_polls_list':latest_polls_list}
    return render(request, 'polls/index.html', context)

def detail(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'polls/detail.html', {'poll': poll})

def results(request, poll_id):
    return HttpResponse("You're looking of the results of poll %s." % poll_id)

def vote(request, poll_id):
    return HttpResponse("You're voting on poll %s." % poll_id)

