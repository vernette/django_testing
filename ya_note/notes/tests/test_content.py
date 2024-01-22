from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

NOTE_TITLE: str = 'Заголовок новости'
NOTE_TEXT: str = 'Текст новости'
NOTE_SLUG: str = 'test'
NOTE_AUTHOR_TEXT: str = 'Автор'
NOTE_READER_TEXT: str = 'Читатель'
NOTES_COUNT: int = 10

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
        """Verifies the context of the notes page for an authenticated user"""
        note = Note.objects.last()
        notes_page_url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(notes_page_url)
        object_list = response.context['object_list']
        self.assertIn(note, object_list)

    def get_object_list(self, url, user):
        """
        Helper method to get the set of notes
        for a specific user on a given page
        """
        notes_page_url = reverse(url)
        self.client.force_login(user)
        response = self.client.get(notes_page_url)
        return set(note for note in response.context['object_list'])

    def test_user_specific_notes(self):
        """
        Verifies that the notes displayed on the page
        are specific to the logged-in user.
        """
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
        """
        Verifies that the note creation and edit pages contain
        a form when accessed by an authenticated user.
        """
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
