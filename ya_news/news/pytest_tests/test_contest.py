from http import HTTPStatus

import pytest

from news.forms import CommentForm
from news.models import Comment

pytestmark = pytest.mark.django_db


LEN_NEWS_ON_PAGE = 10
TEST_COMMENT_TEXT = 'Тестовый комментарий'


def test_home_page_news_count(client, urls):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(urls['home'])
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['news_items']) <= LEN_NEWS_ON_PAGE


def test_home_page_news_order(client, news, urls):
    """Новости отсортированы от самой свежей к самой старой."""
    response = client.get(urls['home'])
    news_list = response.context['news_items']

    for new in range(len(news_list)):
        assert news_list[new] == news[new]


def test_comments_order_on_news_detail(author_client, news_instance,
                                       comments, urls):
    """Сортировка комментариев в хронологическом порядке."""
    response = author_client.get(urls['detail'](news_instance.id))

    assert 'form' in response.context
    comments_list = response.context['comments']

    assert len(comments_list) == len(comments)
    for i, comment in enumerate(comments):
        assert comments_list[i] == comment


def test_comment_form_availability_for_anonymous_user(client, news, urls):
    """Доступность формы для анонимного пользователя."""
    first_news = news[0]
    response = client.get(urls['detail'](first_news.id))
    assert 'comment_form' not in response.context


def test_comment_form_availability_for_authorized_user(author_client,
                                                       news_instance, urls):
    """Доступность формы для авторизованного пользователя."""
    response = author_client.get(urls['detail'](news_instance.id))

    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_comment_creation_for_authorized_user(author_client,
                                              news_instance, urls):
    """Создание комментария для авторизованного пользователя."""
    response = author_client.post(urls['detail'](news_instance.id),
                                  {'text': TEST_COMMENT_TEXT})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(
        news=news_instance, text=TEST_COMMENT_TEXT).exists()


def test_comment_creation_for_anonymous_user(client, news, urls):
    """Создание комментария для анонимного пользователя."""
    first_news = news[0]
    response = client.post(urls['detail'](first_news.id),
                           {'text': TEST_COMMENT_TEXT})
    assert response.status_code == HTTPStatus.FOUND
