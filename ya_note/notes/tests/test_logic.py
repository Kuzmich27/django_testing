from django.test import TestCase
from django.contrib.auth.models import User
from notes.models import Note
from django.urls import reverse
from pytils.translit import slugify


class LogicTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_authenticated_user_can_create_note(self):
        response = self.client.post(reverse('notes:add'),
                                    {'title': 'New Note', 'text': 'Content'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.first().title, 'New Note')

    def test_anonymous_user_cannot_create_note(self):
        self.client.logout()
        response = self.client.post(reverse('notes:add'),
                                    {'title': 'New Note', 'text': 'Content'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 0)

    def test_unique_slug(self):
        self.client.post(reverse('notes:add'),
                         {'title': 'First Note', 'text': 'Content'})
        response = self.client.post(reverse('notes:add'),
                                    {'title': 'First Note', 'text': 'Content'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.count(), 1)

    def test_slug_auto_generation(self):
        response = self.client.post(reverse('notes:add'),
                                    {'title': 'Note Without Slug',
                                     'text': 'Content'}
                                    )
        self.assertEqual(response.status_code, 302)
        note = Note.objects.first()
        self.assertEqual(note.slug, slugify(note.title))

    def test_user_can_edit_own_note(self):
        note = Note.objects.create(
            title='Editable Note', text='Content', author=self.user
        )
        response = self.client.post(reverse(
            'notes:edit', args=[note.slug]),
            {'title': 'Updated Note', 'text': 'Updated Content'})
        self.assertEqual(response.status_code, 302)
        note.refresh_from_db()
        self.assertEqual(note.title, 'Updated Note')

    def test_user_cannot_edit_other_user_note(self):
        other_user = User.objects.create_user(
            username='otheruser', password='otherpass'
        )
        note = Note.objects.create(
            title='Other User Note', text='Content', author=other_user
        )
        response = self.client.post(reverse(
            'notes:edit', args=[note.slug]),
            {'title': 'Updated Note', 'text': 'Updated Content'}
        )
        self.assertEqual(response.status_code, 404)

    def test_user_can_delete_own_note(self):
        note = Note.objects.create(
            title='Deletable Note', text='Content', author=self.user
        )
        response = self.client.post(reverse('notes:delete', args=[note.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cannot_delete_other_user_note(self):
        other_user = User.objects.create_user(
            username='otheruser', password='otherpass'
        )
        note = Note.objects.create(
            title='Other User Note', text='Content', author=other_user
        )
        response = self.client.post(reverse('notes:delete', args=[note.slug]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Note.objects.count(), 1)
