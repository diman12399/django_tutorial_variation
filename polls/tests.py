# -*- encoding:utf-8 -*-
import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from polls.models import Poll, Choice, User


class PollMethodTests(TestCase):

    def test_was_published_recently_with_future_poll(self):
        """
        was_published_recently() should return False for polls whose
        pub_date is in the future
        """
        future_poll = Poll(pub_date=timezone.now()
                           + datetime.timedelta(days=30))
        self.assertEqual(future_poll.was_published_recently(), False)

    def test_was_published_recently_with_old_poll(self):
        """
        was_published_recently() should return False for polls whose
        pub_date is older than 1 day
        """
        old_poll = Poll(pub_date=timezone.now() - datetime.timedelta(days=30))
        self.assertEqual(old_poll.was_published_recently(), False)

    def test_was_published_recently_with_recent_poll(self):
        """
        was_published_recently() should return True for polls whose
        pub_date is within the last day
        """
        #Wrong for time between 00 and 01 hours
        #But tutorial is tutorial
        recent_poll = Poll(pub_date=timezone.now()
                           - datetime.timedelta(hours=1))
        self.assertEqual(recent_poll.was_published_recently(), True)


def create_poll(question, days, order=0):
    """
    Creates a poll with the given `question` published the given number of
    `days` offset to now (negative for polls published in the past,
    positive for polls that have yet to be published).
    """
    return Poll.objects.create(question=question,
                               pub_date=timezone.now()
                               + datetime.timedelta(days=days),
                               order=order)


class PollViewsTests(TestCase):
    def test_index_view_with_no_polls(self):
        """
        If no polls exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_polls_list'], [])

    def test_index_view_with_a_past_poll(self):
        """
        Polls with a pub_date in the past should be
        displayed on the index page.
        """
        create_poll(question="Past poll.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_polls_list'],
            ['<Poll: Past poll.>']
        )

    def test_index_view_with_a_future_poll(self):
        """
        Polls with a pub_date in the future should not be displayed
        on the index page.
        """
        create_poll(question="Future poll.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['latest_polls_list'], [])

    def test_index_view_with_future_poll_and_past_poll(self):
        """
        Even if both past and future polls exist, only past polls should be
        displayed.
        """
        create_poll(question="Past poll.", days=-30)
        create_poll(question="Future poll.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_polls_list'],
            ['<Poll: Past poll.>']
        )

    def test_index_view_with_two_past_polls(self):
        """
        The polls index page may display multiple polls.
        """
        create_poll(question="Past poll 1.", days=-30)
        create_poll(question="Past poll 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_polls_list'],
            ['<Poll: Past poll 2.>', '<Poll: Past poll 1.>']
        )


class PollIndexDetailTest(TestCase):
    def test_detail_view_with_a_future_poll(self):
        """
        The detail view of a poll with a pub_date in the future should
        return a 404 not found.
        """
        future_poll = create_poll(question='Future poll.', days=5)
        response = self.client.get(reverse('polls:detail',
                                   args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_poll(self):
        """
        The detail view of a poll with a pub_date in the past should display
        the poll's question.
        """
        past_poll = create_poll(question='Past poll.', days=-5)
        response = self.client.get(reverse('polls:detail',
                                           args=(past_poll.id,)))
        self.assertContains(response, past_poll.question, status_code=200)


def fill_polls_and_choice():
    for i in range(5):
        poll = create_poll(question='question %d' % i, days=-1, order=i)
        for j in range(3):
            Choice.objects.create(choice_text='choice %d' % j, poll=poll)


class QuestionnaireTest(TestCase):
    def test_questionnaire_sequence(self):
        fill_polls_and_choice()
        response = self.client.get(reverse('polls:questionnaire'))
        for i in range(5, -1):
            poll = Poll.latest_polls()[i]
            self.assertContains(response, poll.question, status_code=200)
            response = response.client.post(reverse('polls:questionnaire'),
                                            {'choice':
                                             poll.choice_set.all()[0]})


class UserSaveTest(TestCase):
    def test_questionnaire_fill(self):
        """
        The user model add latest polls to questionnaire model
        """
        fill_polls_and_choice()
        user = User.objects.create()
        self.assertEqual(len(user.questionnaire_set.all()), 5)


class ClearCookieTest(TestCase):
    def test_clear_cookie(self):
        """
        The clear cookie test.
        """
        fill_polls_and_choice()
        response = self.client.get(reverse('polls:questionnaire'))
        self.assertTrue('id' in response.client.cookies)
        response = self.client.get(reverse('polls:clear_cookie'))
        self.assertEqual('', response.client.cookies['id'].value)
