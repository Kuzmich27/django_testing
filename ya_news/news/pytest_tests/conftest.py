import pytest

from django.test.client import Client

from datetime import datetime

from news.models import News

from django.contrib.auth import get_user_model


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username='testuser', password='testpassword')


@pytest.fixture
@pytest.mark.django_db
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
@pytest.mark.django_db
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client, author


@pytest.fixture
def not_author_client():
    return Client()


@pytest.fixture
@pytest.mark.django_db
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
        date=datetime.today(),
    )
    return news
