from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

NOTE_TITLE: str = 'Заголовок заметки'
NOTE_TEXT: str = 'Текст заметки'
NOTE_SLUG: str = 'test'
NOTE_AUTHOR_TEXT: str = 'Автор'
NOTE_READER_TEXT: str = 'Читатель'

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=NOTE_AUTHOR_TEXT)
        cls.reader = User.objects.create(username=NOTE_READER_TEXT)
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author
        )

    def test_home_page_for_anonymous_user(self):
        """Verifies that the home page is accessible for an anonymous user"""
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_accessible_pages(self):
        """Verifies that certain pages are accessible for an logged-in user"""
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                self.client.force_login(self.reader)
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_detail_edit_and_delete_for_author(self):
        """
        Verifies that note detail, edit, and delete pages are accessible
        for the author and not for the other user
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Verifies that certain pages redirect to the
        login page for an anonymous client
        """
        login_url = reverse('users:login')
        slug = (self.note.slug,)
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', slug),
            ('notes:delete', slug),
            ('notes:edit', slug)
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_auth_pages_accessibility(self):
        """Verifies that auth-related pages are accessible for anon user"""
        auth_urls = (
            ('users:signup', None),
            ('users:login', None),
            ('users:logout', None),
        )
        for name, args in auth_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
