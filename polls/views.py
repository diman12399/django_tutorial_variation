# -*- encoding:utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from polls.models import Poll, Choice, User


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_polls_list'

    def get_queryset(self):
        """
        Return the last five published polls (not including those set to be
        published in the future).
        """
        return Poll.latest_polls()


class DetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/detail.html'
    
    def get_queryset(self):
        """
        Excludes any polls that aren't published yet
        """
        return Poll.objects.filter(pub_date__lte=timezone.now())



class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'

def vote_action(request, poll, no_choice_action, sucess_choice_action):
    try:
        selected_choice = poll.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return no_choice_action()
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return sucess_choice_action()

def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    def no_choice(poll=p):
        return render(request, 'polls/detail.html', {
            'poll': poll,
            'error_message': "You didn't select a choice.",
        })
    def choice(poll=p):
        return HttpResponseRedirect(reverse('polls:results', args=(poll.id,)))

    return vote_action(request, p, no_choice, choice)

def questionnaire(request):
    try:
        p = get_object_or_404(User, pk=request.COOKIES['id'])
    except KeyError:
        p = User.objects.create() 
    polls = p.questionnaire_set.filter(choice__isnull=True).order_by('poll__order')

    if len(polls) > 0:
        def no_choice(poll=polls[0].poll):
            return render(request, 'polls/questionnaire.html', {
                'poll': poll,
                'error_message': "You didn't select a choice.",
            })
        def choice():
            polls[0].choice=Choice.objects.get(pk=request.POST['choice'])
            polls[0].save()
            return HttpResponseRedirect(reverse('polls:questionnaire'))

        response = vote_action(request, polls[0].poll, no_choice, choice)
        response.set_cookie('id', p.id)
    else:
        response = render(request, 'polls/user_results.html', {
            'questionnaire': p.questionnaire_set.all(),
        })
    return response 

def clear_cookie(request):
    response = HttpResponseRedirect(reverse('polls:index'))
    response.delete_cookie('id')
    return response
