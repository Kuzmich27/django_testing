from datetime import datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse

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
def urls():
    """Фикстура для URL-адресов."""
    return {
        'home': reverse('news:home'),
        'detail': lambda news_id: reverse('news:detail', args=(news_id,))
    }


@pytest.fixture
@pytest.mark.django_db
def news():
    """Создает несколько новостей для тестов."""
    len_news_on_page = 10
    base_date = datetime(2025, 3, 5)
    news_items = [
        News(
            title=f'Заголовок {new + 1}',
            date=base_date - timedelta(days=new)
        )
        for new in range(len_news_on_page)
    ]
    News.objects.bulk_create(news_items)
    return News.objects.all()


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
        Comment(news=news_instance, author=author,
                text=f'Комментарий {comment + 1}')
        for comment in range(num_comments)
    ]
    Comment.objects.bulk_create(comments_list)
    return Comment.objects.filter(news=news_instance)
