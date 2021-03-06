from django.conf.urls import url

from .views import (PinCreateView, PinDetailView, PinUpdateView, PinDeleteView, PinImageView,
                    UnpinImageView, PinsByTagView, LikePinImageView, DislikePinImageView)

app_name = 'pins'
urlpatterns = [
    # url(r'^$', UsersListView.as_view(), name='users'),
    url(r'^create/$', PinCreateView.as_view(), name='create'),
    url(r'^tag/(?P<slug>[0-9A-Za-z_\-]+)$', PinsByTagView.as_view(), name='by_tag'),
    url(r'^(?P<slug>[0-9A-Za-z_\-]+)/$', PinDetailView.as_view(), name='detail'),
    url(r'^(?P<slug>[0-9A-Za-z_\-]+)/pinit/$', PinImageView.as_view(), name='pin_image'),
    url(r'^(?P<slug>[0-9A-Za-z_\-]+)/unpinit/$', UnpinImageView.as_view(), name='unpin_image'),
    url(r'^(?P<slug>[0-9A-Za-z_\-]+)/update/$', PinUpdateView.as_view(), name='update'),
    url(r'^(?P<slug>[0-9A-Za-z_\-]+)/delete/$', PinDeleteView.as_view(), name='delete'),
    url(r'^(?P<slug>[0-9A-Za-z_\-]+)/like/$', LikePinImageView.as_view(), name='like'),
    url(r'^(?P<slug>[0-9A-Za-z_\-]+)/dislike/$', DislikePinImageView.as_view(), name='dislike'),
]