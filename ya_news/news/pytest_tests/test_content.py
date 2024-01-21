import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import News

NEWS_TITLE = 'Заголовок новости'
NEWS_TEXT = 'Текст новости'


@pytest.mark.django_db
def test_number_of_news_on_home_page(client):
    News.objects.bulk_create(
        News(title=f'{NEWS_TITLE} {i}', text=f'{NEWS_TEXT} {i}')
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    response = client.get(reverse('news:home'))
    assert (
        len(response.context['object_list'])
        == settings.NEWS_COUNT_ON_HOME_PAGE
    )


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
    )
)
@pytest.mark.django_db
def test_comments_order(client, news_with_comments, name, args):
    detail_url = reverse('news:detail', args=args)
    response = client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_news_order(client):
    News.objects.bulk_create(
        News(
            title=f'{NEWS_TITLE} {i}',
            text=f'{NEWS_TEXT} {i}',
            date=timezone.now() - timezone.timedelta(days=i)
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_id_for_args):
    detail_url = reverse('news:detail', args=news_id_for_args)
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(news_id_for_args, author_client):
    detail_url = reverse('news:detail', args=news_id_for_args)
    response = author_client.get(detail_url)
    assert 'form' in response.context
