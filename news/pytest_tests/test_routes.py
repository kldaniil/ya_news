from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', lazy_fixture('news_id_for_args')),
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expeted_status',
    (
        (lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (lazy_fixture('author_client'), HTTPStatus.OK),
    )
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('comments_id_for_args')),
        ('news:delete', lazy_fixture('comments_id_for_args')),
    )
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client,
    expeted_status,
    name,
    args
):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expeted_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('comments_id_for_args')),
        ('news:delete', lazy_fixture('comments_id_for_args')),
    )
)
def test_redirect_for_anonymous_client(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
