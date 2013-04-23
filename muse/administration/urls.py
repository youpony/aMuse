from django.conf.urls import patterns, url

from muse.administration import views

from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns(
    'muse.administration.views',
    url(
        r'^$',
        views.ExhibitionList.as_view(),
        name='exhibitions_list'
    ),
    url(
        r'^exhibitions/add$',
        views.ExhibitionCreate.as_view(),
        name='exhibition_add'
    ),
    url(
        r'^exhibitions/edit/(?P<pk>\d+)/$',
        views.ExhibitionEdit.as_view(),
        name='exhibition_edit'
    ),
    url(
        r'^exhibitons/delete/(?P<pk>\d+)/$',
        views.ExhibitionDelete.as_view(),
        name='exhibition_delete'
    ),
    url(
        r'^items/list/(?P<pk>\d+)/$',
        views.ItemList.as_view(),
        name='items_list'
    ),
    url(
        r'^items/add/(?P<exhibition_pk>\d+)/',
        views.ItemCreate.as_view(),
        name='item_add'
    ),
    url(
        r'^items/edit/(?P<exhibition_pk>\d+)/(?P<pk>\d+)/$',
        views.ItemEdit.as_view(),
        name='item_edit'
    ),
    url(
        r'^items/delete/(?P<exhibition_pk>\d+)/(?P<pk>\d+)/$',
        views.ItemDelete.as_view(),
        name='item_delete'
    ),
    url(
        r'^items/no_exhibition/$',
        views.ItemWithoutExhibition.as_view(),
        name='item_no_exhibition'
    ),
    url(
        r'^items/edit/(?P<pk>\d+)/$',
        views.ItemEdit.as_view(success_url=reverse_lazy('item_no_exhibition')),
        name='item_no_exhibition_edit'
    ),
    url(
        r'^items/delete/(?P<pk>\d+)/$',
        views.ItemDelete.as_view(
            success_url=reverse_lazy('item_no_exhibition')
        ),
        name='item_no_exhibition_delete'
    ),
)

urlpatterns += patterns(
    '',
    url(
        r'^login/$',
        'django.contrib.auth.views.login',
        {'template_name': 'authentication/login.html'},
        name='login'
    ),
    url(
        r'^logout/$',
        'django.contrib.auth.views.logout',
        {'template_name': 'authentication/logout.html'},
        name='logout'
    ),
)
