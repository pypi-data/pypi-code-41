from django.conf.urls import url
from .views import TagUnsubscribeView


urlpatterns = [
    url(
        r'^email-tag/(?P<hash>.+)/unsubscribe/$',
        TagUnsubscribeView.as_view(),
        name='email_tag_unsubscribe'
    )
]
