from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


class ContentTestCase(TestCase):

    USERNAME = 'testuser'
    PASSWORD = 'testpass'
    OTHER_USERNAME = 'otheruser'
    OTHER_PASSWORD = 'otherpass'
    NOTE_TITLE = 'Test Note'
    NOTE_TEXT = 'Test Content'
    OTHER_USER_NOTE_TITLE = 'Other User Note'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=cls.USERNAME, password=cls.PASSWORD
        )

    def setUp(self):
        self.note = Note.objects.create(
            title=self.NOTE_TITLE, text=self.NOTE_TEXT, author=self.user
        )
        self.URLS = {
            'notes_list': reverse('notes:list'),
            'notes_add': reverse('notes:add'),
            'notes_edit': reverse('notes:edit', args=[self.note.slug])
        }

    def test_note_passed_to_context(self):
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(self.URLS['notes_list'])
        self.assertIn(self.note, response.context['object_list'])

    def test_user_notes_exclusion(self):
        other_user = User.objects.create_user(
            username=self.OTHER_USERNAME, password=self.OTHER_PASSWORD
        )
        Note.objects.create(
            title=self.OTHER_USER_NOTE_TITLE, text='Content', author=other_user
        )
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(self.URLS['notes_list'])
        self.assertNotIn(
            self.OTHER_USER_NOTE_TITLE,
            [note.title for note in response.context['object_list']]
        )

    def test_forms_passed_to_create_edit_pages(self):
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(self.URLS['notes_add'])
        self.assertIsInstance(response.context['form'], NoteForm)

        response = self.client.get(self.URLS['notes_edit'])
        self.assertIsInstance(response.context['form'], NoteForm)
