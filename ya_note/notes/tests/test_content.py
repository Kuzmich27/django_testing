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

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser', password='testpass'
        )

    def setUp(self):
        self.note = Note.objects.create(
            title='Test Note', text='Test Content', author=self.user
        )
        self.URLS = {
            'notes_list': reverse('notes:list'),
            'notes_add': reverse('notes:add'),
            'notes_edit': reverse('notes:edit', args=[self.note.slug])
        }

    def test_note_passed_to_context(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.URLS['notes_list'])
        self.assertIn(self.note, response.context['object_list'])

    def test_user_notes_exclusion(self):
        other_user = User.objects.create_user(
            username='otheruser', password='otherpass'
        )
        Note.objects.create(
            title='Other User Note', text='Content', author=other_user
        )
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.URLS['notes_list'])
        self.assertNotIn(
            'Other User Note',
            [note.title for note in response.context['object_list']]
        )

    def test_forms_passed_to_create_edit_pages(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.URLS['notes_add'])
        self.assertIsInstance(response.context['form'], NoteForm)

        response = self.client.get(self.URLS['notes_edit'])
        self.assertIsInstance(response.context['form'], NoteForm)
