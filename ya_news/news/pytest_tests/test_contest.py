from http import HTTPStatus

import pytest
from django.urls import reverse
from news.models import Comment
from news.forms import CommentForm


pytestmark = pytest.mark.django_db
LEN_NEWS_ON_PAGE = 10


def test_home_page_news_count(client):
    """Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['news_items']) <= LEN_NEWS_ON_PAGE


def test_home_page_news_order(client, news):
    """Новости отсортированы от самой свежей к самой старой."""
    url = reverse('news:home')
    response = client.get(url)
    news_list = response.context['news_items']

    assert news_list[0] == news[0]
    assert news_list[1] == news[1]
    assert news_list[2] == news[2]
    assert news_list[3] == news[3]
    assert news_list[4] == news[4]


def test_comments_order_on_news_detail(author_client, news_instance, comments):
    """Сортировка комментариев в хронологическом порядке."""
    url = reverse('news:detail', args=(news_instance.id,))
    response = author_client.get(url)

    assert 'form' in response.context
    comments_list = response.context['comments']

    assert len(comments_list) == len(comments)
    for i, comment in enumerate(comments):
        assert comments_list[i] == comment


def test_comment_form_availability_for_anonymous_user(client, news):
    """Доступность формы для анонимного пользователя."""
    first_news = news[0]
    url = reverse('news:detail', args=(first_news.id,))
    response = client.get(url)
    assert 'comment_form' not in response.context


def test_comment_form_availability_for_authorized_user(author_client,
                                                       news_instance):
    """Доступность формы для авторизованного пользователя."""
    url = reverse('news:detail', args=(news_instance.id,))
    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_comment_creation_for_authorized_user(author_client, news_instance):
    """Создание комментария для авторизованного пользователя."""
    url = reverse('news:detail', args=(news_instance.id,))
    response = author_client.post(url, {'text': 'Тестовый комментарий'})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(
        news=news_instance, text='Тестовый комментарий').exists()


def test_comment_creation_for_anonymous_user(client, news):
    """Создание комментария для анонимного пользователя."""
    first_news = news[0]
    url = reverse('news:detail', args=(first_news.id,))
    response = client.post(url, {'text': 'Тестовый комментарий'})
    assert response.status_code == HTTPStatus.FOUND
