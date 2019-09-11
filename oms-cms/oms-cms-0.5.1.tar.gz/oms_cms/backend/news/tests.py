from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from oms_cms.backend.languages.models import get_sentinel_lang
from .models import Category, Post, Tags


class ViewsTestCase(TestCase):

    def setUp(self):
        self.now = timezone.now()
        self.yesterday = self.now - timedelta(days=1)
        self.tomorrow = self.now + timedelta(days=1)
        lang = get_sentinel_lang()

        parent = Category.objects.create(name="TestCategory", lang=lang, slug='a')
        children = Category.objects.create(name="ChildrenCategory", parent=parent, lang=lang, slug='b')
        Post.objects.create(
            title="TestPost",
            category=parent,
            lang=lang,
            published_date=self.now,
            slug='c'
        )
        Post.objects.create(
            title="TestNews",
            category=children,
            lang=lang,
            published_date=self.now,
            slug='d'
        )

    def test_post_list(self):
        response = self.client.get(reverse('news:all-news'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['post_list'], ['<Post: TestPost>', '<Post: TestNews>'])

    def test_category_post_list(self):
        response = self.client.get(reverse('news:list-news', kwargs={"slug": "a"}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['post_list'], ['<Post: TestPost>'])

    def test_category_post_detail(self):
        response = self.client.get(reverse('news:new-detail', kwargs={"category": "b", "post": "d"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post'].title, 'TestNews')
