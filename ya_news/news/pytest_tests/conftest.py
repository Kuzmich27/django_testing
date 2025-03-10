from datetime import datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client
from news.models import News, Comment


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
    news_items = []
    for i in range(10):
        news_date = datetime(2025, 3, 5) - timedelta(days=i)
        news_item = News.objects.create(title=f'Заголовок {i + 1}',
                                        date=news_date)
        news_items.append(news_item)
    return news_items


@pytest.fixture
def news_instance():
    """Создает экземпляр новости для тестов."""
    return News.objects.create(title='Заголовок', text='Текст новости')


@pytest.fixture
def comments(author, news_instance):
    """Создает заданное количество комментариев для новости."""
    num_comments = 3
    comments_list = []

    for i in range(num_comments):
        comment = Comment.objects.create(
            news=news_instance,
            author=author,
            text=f'Комментарий {i + 1}'
        )
        comments_list.append(comment)

    return comments_list
