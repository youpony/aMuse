from django.conf.urls import patterns, url

urlpatterns = patterns(
    'muse.papacastoro.views',
    url(r'(?P<public_id>\w+)/$', 'tour', name='tour'),
)

