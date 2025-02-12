from http import HTTPStatus

import pytest

from pytest_django.asserts import assertFormError, assertRedirects

from django.urls import reverse

from news.models import News, Comment
from news.forms import CommentForm, BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(anonymous_client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = anonymous_client.post(url, data=form_data)
    login_url = reverse('users:login')
    redirect_url = f'{login_url}?next={url}'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, news_id_for_args, form_data):
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == form_data['news']
    assert comment.author == form_data['author']


def test_user_cant_use_bad_words(
    not_author_client, news_id_for_args, form_data
):
    url = reverse('news:detail', args=news_id_for_args)
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст.'
    response = not_author_client.post(url, data=form_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_edit_comments_of_other_user(
    not_author_client, form_data, comments, comments_id_for_args
):
    url = reverse('news:edit', args=comments_id_for_args)
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment = Comment.objects.get()
    assert comment.text == comments.text
    assert comment.news == comments.news
    assert comment.author == comments.author


def test_author_can_edit_comment(
    author_client, comments, form_data, comments_id_for_args, comments_url
):
    url = reverse('news:edit', args=comments_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, comments_url)
    comments.refresh_from_db()
    assert comments.text == form_data['text']
    assert comments.news == form_data['news']
    assert comments.author == form_data['author']


def test_user_cant_delete_comment_of_another_user(
    not_author_client, comments_id_for_args, form_data
):
    url = reverse('news:delete', args=comments_id_for_args)
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_delete_comments(
    author_client, form_data, comments_id_for_args, comments_url
):
    url = reverse('news:delete', args=comments_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, comments_url)
    assert Comment.objects.count() == 0
