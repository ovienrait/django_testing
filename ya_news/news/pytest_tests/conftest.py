import pytest

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.test.client import Client

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def all_news():
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=timezone.now() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def id_for_news(news):
    return (news.id,)


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def all_comments(news, author):
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}'
        )
        comment.created = timezone.now() + timedelta(days=index)
        comment.save()


@pytest.fixture
def id_for_comment(comment):
    return (comment.news.id,)


@pytest.fixture
def url_to_comments(news):
    url = reverse('news:detail', args=(news.id,))
    return f'{url}#comments'


@pytest.fixture
def form_data():
    return {'text': 'Новый текст комментария'}
