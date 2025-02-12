import pytest

from django.test.client import Client

from news.models import Comment, News


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


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
        text='Текст комментария',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def comments_id_for_args(comments):
    return (comments.id,)
