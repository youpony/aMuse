# coding: utf-8
"""
API in json
 √ tutte le mostre  GET /m/
 x creare mostra POST /m/
 √ dettagli mostra  GET /m/<id>/
 x edit mostra  PUT /m/<id>/
 x remove mostra  DELETE /m/<id>/ piuttosto data inizio e data fine...
 √ tutti gli oggetti di una data mostra  GET /m/<id>/o/
 x creare oggetto POST /o/
 √ dettagli oggetto  GET /o/<id>/
 x edit oggetto  PUT /o/<id>/
 √ inviare i preferiti segnati POST /s/
 √ link pubblico visualizzazione story GET /s/<numero_casuale>/
 - link per edit storytelling PUT /s/<numero_casuale>/

"""
import datetime
import hashlib
import base64
import simplejson as json

from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.http import Http404, HttpResponseBadRequest
from django.core.files.base import ContentFile
from ajaxutils.decorators import ajax
from ajaxutils.views import AjaxMixin

from muse.rest import models


@ajax(require_GET=True)
def exhibitions_publiclist(request):
    """
    GET /api/m/
    """
    response = []

    exhibitions = \
        models.Exhibition.objects.filter(
            end_date__gte=datetime.date.today()
        ).order_by('start_date')

    for e in exhibitions:
        response.append({
            'pk': e.pk,
            'title': e.title,
            'description': e.description,
            'image': request.build_absolute_uri(e.image.url),
        })

    return {'data': list(response)}


@ajax(require_GET=True)
def exhibition_details(request, pk):
    """
    GET /api/m/<pk>/
    Return all public informations about the selected exhibition.
    """
    exhibition = get_object_or_404(models.Exhibition, pk=pk)
    response = model_to_dict(
        exhibition,
        fields=('title', 'description', 'video')
    )
    # XXX. find a better way to serialize these keys.
    response['museum'] = {
        'id': exhibition.museum.pk,
        'name': exhibition.museum.name
    }
    response['start_date'] = str(exhibition.start_date)
    response['end_date'] = str(exhibition.end_date)
    response['image'] = str(exhibition.image)

    return response


@ajax(require_GET=True)
def exhibition_items(request, pk):
    """
    GET /api/m/<pk>/o/
    Return a list of available objects
    """
    e = get_object_or_404(models.Exhibition, pk=pk)  # TODO[ml]: ?
    items = models.Item.objects.filter(
        exhibitions__pk__contains=pk
    ).order_by('name').values('pk', 'name', )

    for item in items:
        item['images'] = [
            request.build_absolute_uri(itemimage.image.url) for itemimage in
            models.ItemImage.objects.filter(item__pk=item['pk'])
        ]

    return {'data': list(items)}


@ajax(require_GET=True)
def item_details(request, pk):
    """
    GET /o/<pk>
    Return a list of available items.
    """
    item = get_object_or_404(models.Item.objects, pk=pk)
    response = model_to_dict(
        item,
        fields=('name', 'desc', 'author', 'year')
    )
    response['exhibitions'] = [{'name': e.title, 'id': e.pk}
                               for e in item.exhibitions.all()]

    response['images'] = [
        request.build_absolute_uri(itemimage.image.url) for itemimage in
        models.ItemImage.objects.filter(item__pk=item.pk)
    ]

    # XXX. remove the 'data' keyword.
    return {'data': response}



class StoryView(AjaxMixin, View):
    def post(self, request, *args, **kwargs):
        """
        POST /s/
        Create a new story.

        Example of json request is:
        {
            name: "User Name",
            email: "user@example.com",
            exhibition: "exhibition public key",
            posts: [
                {
                    item_pk:  "item public key",
                    image: "image/base64 image",
                },
            ]
        }
        """
        name = request.POST.get('name')
        email = request.POST.get('email')
        exhibition = request.POST.get('exhibition')
        posts = json.loads(request.POST.get('posts', '[]'))

        if not all((name, email, exhibition, posts)):
            return HttpResponseBadRequest('name, email, exhibition or posts fileds invalid.')

        exhibition = get_object_or_404(models.Exhibition, pk=exhibition)
        t = models.Tour(name=name, email=email, exhibition=exhibition)
        t.save()

        for i, post in enumerate(posts):
            item = post.get('item_pk')
            if item:
                item = get_object_or_404(models.Item, pk=item)

            image = post.get('image')
            if image:
                image = ContentFile(base64.decodestring(image))

            if not image and not item:
                return HttpResponseBadRequest()

            p = models.Post(ordering_index=i, tour=t, item=item, image=image)
            p.save()

        # fire up the notification system
        # TODO. fire using django's Signals, not directly.
        models.notify_email(sender='story_view',
                            tour=t,
                            url=lambda pk: request.build_absolute_uri(
                                'storyteller/{0}/'.format(pk)),
        )
        return {'status': 'completed'}

    def get(self, request, pk):
        """
        GET /s/<pk>
        """
        edit = bool(request.GET.get('edit', False) in ('true', 'yes', 'True'))
        if edit:
            tour = get_object_or_404(models.Tour, private_id=pk)
        else:
            tour = get_object_or_404(models.Tour, public_id=pk)

        response = {
            'name': tour.name,
            'exhibition': tour.exhibition.pk,
            'timestamp': tour.timestamp,
        }
        response['posts'] = []
        for p in tour.post_set.all():
            # build json for item
            if p.item:
                item = ('name', 'desc', 'author', 'year')
                item = {key: getattr(p.item, key) for key in item}
                item['images'] = [
                    request.build_absolute_uri(itemimage.url)
                    for itemimage in models.ItemImage.objects.filter(
                        item__pk=p.item.pk
                    )
                ]
            else:
                item = {}

            image = request.build_absolute_uri(p.image.url) if p.image else ''

            response['posts'].append(json.dumps({
                'item': json.dumps(item),
                'image': image,
                'text': p.text,
                'ordering_index': p.ordering_index
            }))

        return response

    def delete(self, request, pk):
        """
        DELETE /s/<pk>
        Delete Tour items.

        """
        tour = get_object_or_404(models.Tour, private_id=pk)
        raise NotImplementedError

    def put(self, request, *args, **kwargs):
        raise NotImplementedError

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(StoryView, self).dispatch(*args, **kwargs)
