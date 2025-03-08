import pytest
from http import HTTPStatus
from django.urls import reverse
from news.models import News, Comment
from datetime import datetime


@pytest.mark.django_db
def test_home_page_news_count(client, news):

    News.objects.bulk_create(
        [News(title=f'Заголовок {i}',
              text='Текст заметки',
              date=datetime.today()) for i in range(15)])
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['news_list']) <= 10


@pytest.mark.django_db
def test_home_page_news_order(client):

    news1 = News.objects.create(title='Заголовок 1', date=datetime(2025, 3, 1))
    news2 = News.objects.create(title='Заголовок 2', date=datetime(2025, 3, 2))
    news3 = News.objects.create(title='Заголовок 3', date=datetime(2025, 3, 3))
    news4 = News.objects.create(title='Заголовок 4', date=datetime(2025, 3, 4))
    news5 = News.objects.create(title='Заголовок 5', date=datetime(2025, 3, 5))

    url = reverse('news:home')
    response = client.get(url)
    news_list = response.context['news_list']

    assert news_list[0] == news5
    assert news_list[1] == news4
    assert news_list[2] == news3
    assert news_list[3] == news2
    assert news_list[4] == news1


@pytest.mark.django_db
def test_comments_order_on_news_detail(author_client, news):
    comment1 = Comment.objects.create(
        news=news, author=author_client[1], text='Комментарий 1')
    comment2 = Comment.objects.create(
        news=news, author=author_client[1], text='Комментарий 2')
    comment3 = Comment.objects.create(
        news=news, author=author_client[1], text='Комментарий 3')

    url = reverse('news:detail', args=(news.id,))
    response = author_client[0].get(url)

    assert 'form' in response.context
    comments_list = response.context['comments']

    assert len(comments_list) == 3
    assert comments_list[0] == comment1
    assert comments_list[1] == comment2
    assert comments_list[2] == comment3


@pytest.mark.django_db
def test_comment_form_availability_for_anonymous_user(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'comment_form' not in response.context


@pytest.mark.django_db
def test_comment_form_availability_for_authorized_user(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client[0].get(url)
    assert 'form' in response.context


@pytest.mark.django_db
def test_comment_creation_for_authorized_user(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client[0].post(url, {'text': 'Тестовый комментарий'})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(
        news=news, text='Тестовый комментарий').exists()


@pytest.mark.django_db
def test_comment_creation_for_anonymous_user(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, {'text': 'Тестовый комментарий'})
    assert response.status_code == HTTPStatus.FOUND
