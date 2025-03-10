from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS
from news.models import Comment


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
def anonimous_and_autouser_send_comment(
    parametrized_client,
    expected_status,
    name,
    comments
):
    """Отправление комментариев анонимным и авторизованным пользователем"""

    url = reverse(name, agrs=(comments.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit')
)
def anonimous_and_autouser_edit_delete_comments(
    parametrized_client,
    expected_status,
    name,
    comments
):
    """Редактирование, удаление своих комментариев авторизированным юзером"""

    url = reverse(name, agrs=(comments.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_forbidden_words(author_client, news_instance, bad_word):
    """Запрещённые слова = не будет опубликовано, а форма вернёт ошибку."""
    bad_word_text = f'Какой-то текст, {bad_word}, еще какой-то текст'

    response = author_client.post(
        reverse('news:detail', kwargs={'pk': news_instance.pk}),
        {'text': bad_word_text}
    )

    assert Comment.objects.filter(text=bad_word_text).count() == 0

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_comment_without_forbidden_words(author_client, news_instance):
    """Авторизированный юзер, редактирование и удаление своих комментариев"""
    valid_comment_text = 'Это допустимый комментарий'

    response = author_client.post(
        reverse('news:detail', kwargs={'pk': news_instance.pk}),
        {'text': valid_comment_text}
    )

    assert response.status_code == HTTPStatus.FOUND

    assert Comment.objects.count() == 1
    assert Comment.objects.first().text == valid_comment_text
