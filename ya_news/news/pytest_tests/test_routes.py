import pytest

from http import HTTPStatus

from django.urls import reverse


from news.models import Comment


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_separate_news_for_anonymous_user(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
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
    name,
    news,
    expected_status,
    not_author
):
    if isinstance(parametrized_client, tuple):
        client, author = parametrized_client
    else:
        client = parametrized_client
        author = None

    if author:
        comment = Comment.objects.create(
            news=news,
            text='Тестовый комментарий',
            author=author
        )
    else:
        comment = Comment.objects.create(
            news=news,
            text='Тестовый комментарий',
            author=not_author
        )
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize('name', ('news:delete', 'news:edit'))
def test_edit_or_delete_comment_for_anonymous_user(
    not_author_client,
    name,
    news,
    not_author
):
    client = not_author_client
    comment = Comment.objects.create(
        news=news,
        text='Тестовый комментарий',
        author=not_author
    )
    url = reverse(name, args=(comment.id,))
    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(reverse('users:login'))
    assert f'?next={url}' in response.url


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit')
)
def test_edit_or_delete_strangers_comment(
    author_client,
    name,
    news,
    not_author
):
    client, _ = author_client
    comment = Comment.objects.create(
        news=news,
        text='Тестовый комментарий',
        author=not_author
    )

    url = reverse(name, args=(comment.id,))
    response = client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
