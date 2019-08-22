import datetime

from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59,
                                                   seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class SimpleTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Every test needs a client.
        cls.client = Client()

    def test_polls(self):
        # Issue a GET request.
        response = self.client.get('/polls/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)


class QuestionIdIsEmpty(TestCase):
    def test_queryset_is_empty_not_exist(self):
        self.assertFalse(Question.objects.filter(id=1).exists())

    def test_all_queryset_is_empty_not_exist(self):
        self.assertFalse(Question.objects.all().exists())

    def test_queryset_is_empty_equal(self):
        self.assertEqual(Question.objects.filter(id=1).count(), 0)

    def test_create_question_and_equal_text(self):
        question = create_question(question_text='test Question.', days=0)
        self.assertEqual('test Question.', question.question_text)

    def test_create_four_question(self):
        create_question(question_text="Past question 1.", days=0)
        create_question(question_text="Past question 2.", days=0)
        create_question(question_text="Past question 3.", days=0)
        create_question(question_text="Past question 4.", days=0)
        self.assertEqual(Question.objects.all().count(), 4)



"""
When in .models - pub_date = models.DateTimeField('date published', 
auto_now_add=True)
"""
# class QuestionModelTest(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         #Set up non-modified objects used by all test methods
#         Question.objects.create(question_text="New Test question.", pub_date=0)
#
#     def test_question_text_label(self):
#         question = Question.objects.get(id=1)
#         field_label = '%s' % (question.question_text)
#         self.assertEquals(field_label, 'New Test question.')
#
#     def test_days_of_label(self):
#         question = Question.objects.get(id=1)
#         days_label = '%s' % (question.pub_date.date())
#         self.assertEquals(days_label, '%s' % question.pub_date.date())
#
#     def test_text_max_length(self):
#         question = Question.objects.get(id=1)
#         max_length = question._meta.get_field('question_text').max_length
#         self.assertEquals(max_length, 200)
#
#     def test_get_absolute_url(self):
#         question = Question.objects.get(id=1)
#         # This will also fail if the urlconf is not defined.
#         self.assertEquals(question.get_absolute_url(), '/polls/1/')


"""For this test need coment QuestionModelTest"""
# class ChoiceModelTest(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         #Set up non-modified objects used by all test methods
#         Question.objects.get_or_create(question_text="New Test question for choice.")
#         Choice.objects.create(choice_text="New Test choice.", votes=2, question_id=1)
#
#     def test_choice_text_label(self):
#         choice = Choice.objects.get(id=1)
#         field_label = '%s' % (choice.choice_text)
#         self.assertEquals(field_label, 'New Test choice.')
#
#     def test_choice_votes_label(self):
#         choice = Choice.objects.get(id=1)
#         self.assertEquals(choice.votes, 2)
#
#     def test_choice_text_max_length(self):
#         choice = Choice.objects.get(id=1)
#         max_length = choice._meta.get_field('choice_text').max_length
#         self.assertEquals(max_length, 200)


"""
I think delete this test
"""
# class QuestionListViewTest(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         number_of_questions = 13
#         for question_num in range(number_of_questions):
#             Question.objects.create(question_text='Question %s' % question_num)
#
#     def test_view_uses_correct_template(self):
#         resp = self.client.get(reverse('polls:index'))
#         self.assertEqual(resp.status_code, 200)
#
#         self.assertTemplateUsed(resp, 'polls/index.html')
#
#     def test_nums_of_question_nums(self):
#         self.assertEqual(len(Question.objects.all()), 13)
#         print(Question.objects.all())
#         for i, j in enumerate(Question.objects.all()):
#             self.assertEqual(('Question ' + str(i)), str(j))
