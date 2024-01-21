from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

NOTE_TITLE = 'Заголовок заметки'
NOTE_TEXT = 'Текст заметки'
NOTE_SLUG = 'test'
NEW_NOTE_TITLE = 'Обновлённый заголовок заметки'
NEW_NOTE_TEXT = 'Обновлённый текст заметки'
NEW_NOTE_SLUG = 'test1'
NOTE_AUTHOR_TEXT = 'Автор'
NOTE_READER_TEXT = 'Читатель'
NOTE_DEFAULT_USER_TEXT = 'Пользователь'
EXPECTED_OPERATION_SUCCESS = 1
EXPECTED_OPERATION_FAILURE = 0


User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username=NOTE_DEFAULT_USER_TEXT)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.client = Client()
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': NOTE_TITLE,
            'text': NOTE_TEXT,
            'slug': NOTE_SLUG,
        }

    def test_note_creation_for_different_users(self):
        user_expected_results = (
            (self.client, EXPECTED_OPERATION_FAILURE),
            (self.auth_client, EXPECTED_OPERATION_SUCCESS),
        )
        for client, expected_count in user_expected_results:
            with self.subTest(client=client):
                client.post(self.url, data=self.form_data)
                notes_count = Note.objects.count()
                self.assertEqual(notes_count, expected_count)
                if expected_count == EXPECTED_OPERATION_SUCCESS:
                    note = Note.objects.get()
                    self.assertEqual(note.title, NOTE_TITLE)
                    self.assertEqual(note.text, NOTE_TEXT)
                    self.assertEqual(note.slug, NOTE_SLUG)

    def test_cannot_create_slug_duplicate(self):
        self.auth_client.post(self.url, data=self.form_data)
        self.form_data['slug'] = Note.objects.get().slug
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(Note.objects.get().slug + WARNING))
        self.assertEqual(Note.objects.count(), EXPECTED_OPERATION_SUCCESS)

    def test_empty_slug(self):
        self.form_data.pop('slug', None)
        expected_slug = slugify(self.form_data['title'])
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), EXPECTED_OPERATION_SUCCESS)
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, expected_slug)


class TestCommentEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=NOTE_AUTHOR_TEXT)
        cls.reader = User.objects.create(username=NOTE_READER_TEXT)
        cls.note = Note.objects.create(
            title=NOTE_TITLE, text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': NEW_NOTE_TITLE,
            'text': NEW_NOTE_TEXT,
            'slug': NEW_NOTE_SLUG
        }

    def test_user_cant_delete_note_of_another_user(self):
        users_expected_results = (
            (self.reader, EXPECTED_OPERATION_SUCCESS),
            (self.author, EXPECTED_OPERATION_FAILURE),
        )
        for user, expected_result in users_expected_results:
            self.client.force_login(user)
            with self.subTest(user=user, expected_result=expected_result):
                self.client.post(self.delete_url)
                notes_count = Note.objects.count()
                self.assertEqual(notes_count, expected_result)

    def test_user_cant_edit_note_of_another_user(self):
        users_expected_results = (
            (self.reader, NOTE_TEXT),
            (self.author, NEW_NOTE_TEXT),
        )
        for user, expected_result in users_expected_results:
            self.client.force_login(user)
            with self.subTest(user=user, expected_result=expected_result):
                self.client.post(self.edit_url, data=self.form_data)
                self.note.refresh_from_db()
                self.assertEqual(self.note.text, expected_result)
