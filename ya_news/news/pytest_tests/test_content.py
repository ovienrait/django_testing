import pytest

from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.parametrize(
    'name', ('news:home',)
)
@pytest.mark.usefixtures('all_news')
@pytest.mark.django_db
def test_news_count(client, name):
    """Проверка количества отображаемых на главной странице новостей"""
    url = reverse(name)
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.parametrize(
    'name', ('news:home',)
)
@pytest.mark.usefixtures('all_news')
@pytest.mark.django_db
def test_news_order(client, name):
    """Проверка сортировки новостей по дате"""
    url = reverse(name)
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_for_news')),
    ),
)
@pytest.mark.usefixtures('all_comments')
@pytest.mark.django_db
def test_comments_order(client, name, args):
    """Проверка сортировки комментариев по дате"""
    url = reverse(name, args=args)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_for_news')),
    ),
)
@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, name, args):
    """Проверка недоступности формы для отправки комментария для
    неавторизованного пользователя
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_for_news')),
    ),
)
@pytest.mark.django_db
def test_authorized_client_has_form(author_client, name, args):
    """Проверка доступности формы для отправки комментария для
    авторизованного пользователя
    """
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
