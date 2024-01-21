from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

NOTE_TITLE = 'Заголовок новости'
NOTE_TEXT = 'Текст новости'
NOTE_SLUG = 'test'
NOTE_AUTHOR_TEXT = 'Автор'
NOTE_READER_TEXT = 'Читатель'
NOTES_COUNT = 10

User = get_user_model()


class TestNotesListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=NOTE_AUTHOR_TEXT)
        cls.reader = User.objects.create(username=NOTE_READER_TEXT)
        Note.objects.bulk_create(
            Note(
                title=NOTE_TITLE,
                text=NOTE_TEXT,
                slug=f'{NOTE_SLUG}{index}',
                author=cls.author
            )
            for index in range(NOTES_COUNT)
        )

    def test_notes_page_context(self):
        note = Note.objects.last()
        notes_page_url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(notes_page_url)
        object_list = response.context['object_list']
        self.assertIn(note, object_list)

    def get_object_list(self, url, user):
        notes_page_url = reverse(url)
        self.client.force_login(user)
        response = self.client.get(notes_page_url)
        return set(note for note in response.context['object_list'])

    def test_user_specific_notes(self):
        notes_page_name = 'notes:list'
        author_notes = self.get_object_list(notes_page_name, self.author)
        reader_notes = self.get_object_list(notes_page_name, self.reader)
        self.assertFalse(author_notes.intersection(reader_notes))


class TestNotesAddAndEdit(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=NOTE_AUTHOR_TEXT)
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author
        )

    def test_note_creation_and_edit_page_have_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                self.client.force_login(self.author)
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
