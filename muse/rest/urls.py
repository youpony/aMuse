from django.conf.urls import patterns, url

urlpatterns = patterns('muse.rest.views',
    url(r'^m$', 'exhibitions_list'),
)
