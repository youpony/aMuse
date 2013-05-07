from django.conf.urls import patterns, url

from muse.papacastoro import views

urlpatterns = patterns(
    'muse.papacastoro.views',
    url(
        r'manage/(?P<private_id>\w+)/$',
        views.PostList.as_view(),
        name='posts_list'
    ),
    url(
        r'delete/(?P<private_id>\w+)/(?P<pk>\w+)/$',
        views.PostDelete.as_view(),
        name='post_delete'
    ),
    url(r'(?P<public_id>\w+)/$', 'tour', name='tour'),
)
