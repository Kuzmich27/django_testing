from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note


class LogicTestCase(TestCase):
    USERNAME = 'testuser'
    PASSWORD = 'testpass'
    OTHER_USERNAME = 'otheruser'
    OTHER_PASSWORD = 'otherpass'
    NOTE_TITLE = 'Test Note'
    NOTE_TEXT = 'Test Content'
    NEW_NOTE_TITLE = 'New Note'
    NEW_NOTE_TEXT = 'Content'
    UPDATED_NOTE_TITLE = 'Updated Note'
    UPDATED_NOTE_TEXT = 'Updated Content'
    OTHER_USER_NOTE_TITLE = 'Other User Note'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username=cls.USERNAME,
                                            password=cls.PASSWORD)

    def setUp(self):
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        self.note = Note.objects.create(title=self.NOTE_TITLE,
                                        text=self.NOTE_TEXT,
                                        author=self.user)
        self.URLS = {
            'notes_list': reverse('notes:list'),
            'notes_add': reverse('notes:add'),
            'notes_edit': reverse('notes:edit', args=[self.note.slug]),
            'notes_delete': reverse('notes:delete', args=[self.note.slug]),
        }

    def test_authenticated_user_can_create_note(self):
        response = self.client.post(self.URLS['notes_add'],
                                    {'title': self.NEW_NOTE_TITLE,
                                     'text': self.NEW_NOTE_TEXT})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 2)
        self.assertEqual(Note.objects.last().title, self.NEW_NOTE_TITLE)

    def test_anonymous_user_cannot_create_note(self):
        self.client.logout()
        response = self.client.post(self.URLS['notes_add'],
                                    {'title': self.NEW_NOTE_TITLE,
                                     'text': self.NEW_NOTE_TEXT})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_unique_slug(self):
        self.client.post(self.URLS['notes_add'],
                         {'title': 'First Note', 'text': self.NEW_NOTE_TEXT})
        response = self.client.post(self.URLS['notes_add'],
                                    {'title': 'First Note',
                                     'text': self.NEW_NOTE_TEXT})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Note.objects.count(), 2)

    def test_slug_auto_generation(self):
        response = self.client.post(
            self.URLS['notes_add'],
            {'title': 'Note Without Slug', 'text': self.NEW_NOTE_TEXT})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note = Note.objects.last()
        self.assertEqual(note.slug, slugify(note.title))

    def test_user_can_edit_own_note(self):
        response = self.client.post(
            self.URLS['notes_edit'],
            {'title': self.UPDATED_NOTE_TITLE, 'text': self.UPDATED_NOTE_TEXT})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.UPDATED_NOTE_TITLE)

    def test_user_cannot_edit_other_user_note(self):
        other_user = User.objects.create_user(
            username=self.OTHER_USERNAME, password=self.OTHER_PASSWORD
        )
        note = Note.objects.create(
            title=self.OTHER_USER_NOTE_TITLE, text=self.NEW_NOTE_TEXT,
            author=other_user
        )
        response = self.client.post(
            reverse('notes:edit', args=[note.slug]),
            {'title': self.UPDATED_NOTE_TITLE, 'text': self.UPDATED_NOTE_TEXT}
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_can_delete_own_note(self):
        response = self.client.post(self.URLS['notes_delete'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cannot_delete_other_user_note(self):
        other_user = User.objects.create_user(
            username=self.OTHER_USERNAME, password=self.OTHER_PASSWORD
        )
        note = Note.objects.create(
            title=self.OTHER_USER_NOTE_TITLE, text=self.NEW_NOTE_TEXT,
            author=other_user
        )
        response = self.client.post(reverse('notes:delete', args=[note.slug]))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 2)
