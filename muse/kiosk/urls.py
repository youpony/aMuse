from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'muse.kiosk.views',
    url(r'^$', 'home', name='home'),
    url(r'(?P<pk>\d+)/$', 'objects', name='objects'),
)
