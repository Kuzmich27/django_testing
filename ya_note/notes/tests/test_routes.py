from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note


class RoutesTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.note = Note.objects.create(
            title='Test Note', text='Test Content', author=self.user
        )

    def test_home_page_accessible_to_anonymous_user(self):
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, 200)

    def test_notes_page_accessible_to_authenticated_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)

    def test_done_page_accessible_to_authenticated_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notes:success'))
        self.assertEqual(response.status_code, 200)

    def test_add_page_accessible_to_authenticated_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notes:add'))
        self.assertEqual(response.status_code, 200)

    def test_note_detail_accessible_to_author(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse(
            'notes:detail', args=[self.note.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_note_detail_not_accessible_to_other_user(self):
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.get(reverse(
            'notes:detail', args=[self.note.slug])
        )
        self.assertEqual(response.status_code, 302)

    def test_redirect_anonymous_user(self):
        response = self.client.get(reverse('notes:list'))
        self.assertRedirects(response, reverse(
            'users:login') + '?next=' + reverse('notes:list'))

    def test_registration_login_logout_accessible_to_all(self):
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)

        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 200)
