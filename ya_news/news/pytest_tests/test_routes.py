from http import HTTPStatus

import pytest
from django.urls import reverse
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_home_availability_for_anonymous_user(client):
    """Главная страница доступна анонимному пользователю."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_separate_news_for_anonymous_user(client, news_instance):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news_instance.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit')
)
def test_comment_availability_for_author(
    parametrized_client,
    expected_status,
    name,
    comments
):
    """Удаления и редактирования комментария доступны автору комментария."""
    comment = comments[0]
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name', ('news:delete', 'news:edit'))
def test_edit_or_delete_comment_for_anonymous_user(
    not_author_client,
    name,
    comments
):
    """Редактирования или удаления комментария анонимным пользователем."""
    comment = comments[0]
    url = reverse(name, args=(comment.id,))
    response = not_author_client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(reverse('users:login'))
    assert f'?next={url}' in response.url


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit')
)
def test_edit_or_delete_strangers_comment(
    name,
    not_author_client,
    news_instance,
    not_author
):
    """Авторизованный не может редактировать и удалять чужие комментарии."""
    comment = Comment.objects.create(
        news=news_instance,
        text='Тестовый комментарий',
        author=not_author
    )
    url = reverse(name, args=(comment.id,))
    response = not_author_client.post(url)

    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """Страницы регистрации пользователей, анонимным пользователям."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
