from datetime import datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client

from news.models import Comment, News


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
    return client


@pytest.fixture
def not_author_client():
    return Client()


@pytest.fixture
@pytest.mark.django_db
def news():
    """Создает несколько новостей для тестов."""
    news_items = [
        News(
            title=f'Заголовок {i + 1}',
            date=datetime(2025, 3, 5) - timedelta(days=i)
        )
        for i in range(10)
    ]
    News.objects.bulk_create(news_items)
    return News.objects.filter(
        title__in=[f'Заголовок {i + 1}' for i in range(10)]
    )


@pytest.fixture
@pytest.mark.django_db
def news_instance():
    """Создает экземпляр новости для тестов."""
    return News.objects.create(title='Заголовок', text='Текст новости')


@pytest.fixture
@pytest.mark.django_db
def comments(author, news_instance):
    """Создает заданное количество комментариев для новости."""
    num_comments = 3
    comments_list = [
        Comment(news=news_instance, author=author, text=f'Комментарий {i + 1}')
        for i in range(num_comments)
    ]
    Comment.objects.bulk_create(comments_list)
    return Comment.objects.filter(news=news_instance)
