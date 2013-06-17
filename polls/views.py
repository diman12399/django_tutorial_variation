# -*- encoding:utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from polls.models import Poll, Choice, User


class IndexView(generic.ListView):
    """
    Index view for site "polls" part,
    show 5 latest polls
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_polls_list'

    def get_queryset(self):
        """
        Return the last five published polls (not including those set to be
        published in the future).
        """
        return Poll.latest_polls()


class DetailView(generic.DetailView):
    """
    Show poll with its choices,
    redirect to results page after submit vote
    """
    model = Poll
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any polls that aren't published yet
        """
        return Poll.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    """
    Show votes for request poll
    """
    model = Poll
    template_name = 'polls/results.html'


def vote_action(request, poll):
    """
    Vote fot poll, add choice to statistic table
    """
    selected_choice = poll.choice_set.get(pk=request.POST['choice'])
    selected_choice.votes += 1
    selected_choice.save()


def vote(request, poll_id):
    """
    Vote for single poll
    """
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        vote_action(request, p)
    except KeyError:
        return render(request, 'polls/detail.html', {
            'poll': poll,
            'error_message': "You didn't select a choice.",
        })
    else:
        return HttpResponseRedirect(reverse('polls:results', args=(poll_id,)))


def generate_questionnaire_poll(request, quest):
    """
    Generate response for questionnaire's qustion
    """
    response = None
    try:
        vote_action(request, quest.poll)
    except KeyError:
        response = render(request, 'polls/questionnaire.html', {
            'poll': quest.poll,
            'error_message': "You didn't select a choice.",
        })
    else:
        quest.choice = Choice.objects.get(pk=request.POST['choice'])
        quest.save()
        response = HttpResponseRedirect(reverse('polls:questionnaire'))

    response.set_cookie('id', quest.user_id.id)
    return response


def generate_questionnaire_result(request, questionnaire_result):
    """
    Generate response for questionnaire's result
    """
    return render(request, 'polls/user_results.html', {
        'questionnaire': questionnaire_result,
    })


def questionnaire(request):
    """
    Complex view for provide questionnaire functionality,
    show unanswered user polls one per page and results page
    """
    try:
        user = get_object_or_404(User, pk=request.COOKIES['id'])
    except KeyError:
        user = User.objects.create()
    questionnaire = (user.questionnaire_set.filter(choice__isnull=True)
                     .order_by('poll__order'))

    if len(questionnaire) > 0:
        return generate_questionnaire_poll(request, questionnaire[0])
    else:
        return generate_questionnaire_result(request,
                                             user.questionnaire_set.all())


def clear_cookie(request):
    """
    Clear user 'id' cookie and redirect to index page
    """
    response = HttpResponseRedirect(reverse('polls:index'))
    response.delete_cookie('id')
    return response
