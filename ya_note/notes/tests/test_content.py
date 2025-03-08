from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note
from notes.forms import NoteForm


class ContentTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.note = Note.objects.create(
            title='Test Note', text='Test Content', author=self.user
        )

    def test_note_passed_to_context(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notes:list'))
        self.assertIn(self.note, response.context['object_list'])

    def test_user_notes_exclusion(self):
        other_user = User.objects.create_user(
            username='otheruser', password='otherpass'
        )
        Note.objects.create(
            title='Other User Note', text='Content', author=other_user
        )
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notes:list'))
        self.assertNotIn(
            'Other User Note',
            [note.title for note in response.context['object_list']]
        )

    def test_forms_passed_to_create_edit_pages(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notes:add'))
        self.assertIsInstance(response.context['form'], NoteForm)

        response = self.client.get(reverse(
            'notes:edit', args=[self.note.slug])
        )
        self.assertIsInstance(response.context['form'], NoteForm)
