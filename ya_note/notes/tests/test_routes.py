from django.contrib.auth.models import User
from django.test import TestCase
from http import HTTPStatus
from django.urls import reverse

from notes.models import Note


class RoutesTestCase(TestCase):

    USERNAME = 'testuser'
    PASSWORD = 'testpass'
    OTHER_USERNAME = 'otheruser'
    OTHER_PASSWORD = 'otherpass'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=cls.USERNAME, password=cls.PASSWORD
        )

    def setUp(self):
        self.other_user = User.objects.create_user(
            username=self.OTHER_USERNAME, password=self.OTHER_PASSWORD
        )
        self.note = Note.objects.create(
            title='Test Note', text='Test Content', author=self.user
        )
        self.URLS = {
            'notes_list': reverse('notes:list'),
            'notes_add': reverse('notes:add'),
            'notes_edit': reverse('notes:edit', args=[self.note.slug]),
            'notes_success': reverse('notes:success'),
            'notes_detail': reverse('notes:detail', args=[self.note.slug]),
            'notes_home': reverse('notes:home'),
        }

    def test_home_page_accessible_to_anonymous_user(self):
        response = self.client.get(self.URLS['notes_home'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_page_accessible_to_authenticated_user(self):
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(self.URLS['notes_list'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_done_page_accessible_to_authenticated_user(self):
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(self.URLS['notes_success'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_add_page_accessible_to_authenticated_user(self):
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(self.URLS['notes_add'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_detail_accessible_to_author(self):
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(reverse(
            'notes:detail', args=[self.note.slug])
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_detail_not_accessible_to_other_user(self):
        self.client.login(
            username=self.OTHER_USERNAME, password=self.OTHER_PASSWORD)
        response = self.client.get(self.URLS['notes_detail'])
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_anonymous_user(self):
        response = self.client.get(self.URLS['notes_list'])
        self.assertRedirects(response, reverse(
            'users:login') + '?next=' + self.URLS['notes_list'])

    def test_registration_login_logout_accessible_to_all(self):
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
