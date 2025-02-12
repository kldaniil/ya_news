from datetime import datetime, timedelta

import pytest

from django.test.client import Client
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from news.models import Comment, News


COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Новый текст комментария'


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def anonymous_client():
    client = Client()
    return client


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
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
        text='Текст новости',
    )
    return news


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def comments(author, news):
    comment = Comment.objects.create(
        text=COMMENT_TEXT,
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def comments_id_for_args(comments):
    return (comments.id,)


@pytest.fixture
def much_news():
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        today = datetime.today()
        all_news = [
            News(
                title=f'Новость {index}',
                text=f'Текст новости {index}.',
                date=today - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
        News.objects.bulk_create(all_news)


@pytest.fixture
def many_comments(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        # Меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data(news, author):
    return {
        'text': NEW_COMMENT_TEXT,
        'author': author,
        'news': news,
    }


@pytest.fixture
def comments_url(news):
    url = reverse('news:detail', args=(news.id,))
    new_url = url + '#comments'
    return new_url
