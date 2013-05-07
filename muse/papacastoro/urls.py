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
        r'add/(?P<private_id>\w+)/$',
        views.PostAddPersonal.as_view(),
        name='post_add'
    ),
    url(
        r'comment/(?P<private_id>\w+)/(?P<pk>\w+)/$',
        views.PostComment.as_view(),
        name='post_comment'
    ),
    url(
        r'delete/(?P<private_id>\w+)/(?P<pk>\w+)/$',
        views.PostDelete.as_view(),
        name='post_delete'
    ),
    url(r'(?P<public_id>\w+)/$', 'tour', name='tour'),
)
