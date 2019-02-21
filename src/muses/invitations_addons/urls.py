from django.conf.urls import url

from . import views

__all__ = (
    'urlpatterns',
)

app_name = 'invitations_addons'
urlpatterns = [
    url(r'^send-invites/success/$', views.SendMultipleInvitesSuccess.as_view(),
        name='send-invites-success'),
    url(r'^send-invites/$', views.SendMultipleInvites.as_view(),
        name='send-invites'),
    url(r'^accept-invite/(?P<key>\w+)/?$', views.AcceptInvite.as_view(),
        name='accept-invite'),
    url(r'^send-invite/$', views.SendInvite.as_view(), name='send-invites'),
]
