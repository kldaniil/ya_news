import pytest
from pytest_lazyfixture import lazy_fixture

from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from news.models import News, Comment
from news.forms import CommentForm


@pytest.mark.django_db
def test_count_and_order_news(client, much_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_detail_page_comments_order(client, news_id_for_args, many_comments):
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, available',
    (
        (lazy_fixture('author_client'), True),
        (lazy_fixture('anonymous_client'), False),
    )
)
@pytest.mark.django_db
def test_detail_page_form_for_user_and_anonymous(
    news_id_for_args, parametrized_client, available
):
    url = reverse('news:detail', args=news_id_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is available
    if 'form' in response.context:
        assert (isinstance(response.context['form'], CommentForm))
