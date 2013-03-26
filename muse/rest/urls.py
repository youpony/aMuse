from django.conf.urls import patterns, url

urlpatterns = patterns(
    'muse.rest.views',
    url('^m/$', 'exhibitions_publiclist', name='exhibitions_publiclist'),
    url(r'^m/(?P<pk>\d+)/$', 'exhibition_details'),
    url(r'^m/(?P<pk>\d+)/o/$', 'exhibition_items'),
    url(r'^o/(?P<pk>\d+)/$', 'item_details'),
    url(r'^s/$', 'story'),
)


