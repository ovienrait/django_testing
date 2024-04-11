import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.parametrize(
    'name, args',
    (('news:detail', pytest.lazy_fixture('id_for_news')),),
)
@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, name, args, form_data):
    """Проверка невозможности отправки комментария анонимным пользователем"""
    url = reverse(name, args=args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'name, args',
    (('news:detail', pytest.lazy_fixture('id_for_news')),),
)
def test_user_can_create_comment(
    author_client, author, name, args, news, form_data
):
    """Проверка возможности отправки комментария авторизованным
    пользователем
    """
    url = reverse(name, args=args)
    assert Comment.objects.count() == 0
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize(
    'name, args',
    (('news:detail', pytest.lazy_fixture('id_for_news')),),
)
def test_user_cant_use_bad_words(author_client, name, args, form_data):
    """Проверка невозможности публикации содержащего запрещённые слова
    комментария
    """
    url = reverse(name, args=args)
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    response = author_client.post(url, data=form_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'name, args',
    (('news:delete', pytest.lazy_fixture('id_for_comment')),),
)
def test_author_can_delete_comment(
    author_client, url_to_comments, name, args
):
    """Проверка возможности удаления авторизованным пользователем своих
    комментариев
    """
    url = reverse(name, args=args)
    response = author_client.delete(url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'name, args',
    (('news:delete', pytest.lazy_fixture('id_for_comment')),),
)
def test_user_cant_delete_comment_of_another_user(
    not_author_client, name, args
):
    """Проверка невозможности удаления авторизованным пользователем чужих
    комментариев
    """
    url = reverse(name, args=args)
    not_author_client.delete(url)
    assert Comment.objects.count() == 1


@pytest.mark.parametrize(
    'name, args',
    (('news:edit', pytest.lazy_fixture('id_for_comment')),),
)
def test_author_can_edit_comment(
    author_client, url_to_comments, name, args, form_data, comment
):
    """Проверка возможности редактирования авторизованным пользователем своих
    комментариев
    """
    url = reverse(name, args=args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.parametrize(
    'name, args',
    (('news:edit', pytest.lazy_fixture('id_for_comment')),),
)
def test_user_cant_edit_comment_of_another_user(
    not_author_client, name, args, form_data, comment
):
    """Проверка невозможности редактирования авторизованным пользователем чужих
    комментариев
    """
    url = reverse(name, args=args)
    not_author_client.post(url, data=form_data)
    comment.refresh_from_db()
    assert comment.text != form_data['text']
