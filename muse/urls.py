from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^k/', include('muse.kiosk.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('muse.rest.urls')),
    url(r'^storyteller/', include('muse.papacastoro.urls')),
    url(r'^administration/', include('muse.administration.urls')),

)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(
            r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}
        ),
    )
