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
 - inviare i preferiti segnati POST /s/
 - link pubblico visualizzazione story GET /s/<numero_casuale>/
 - link per edit storytelling PUT /s/<numero_casuale>/

"""
import datetime
import hashlib
import base64
import simplejson as json

from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponseBadRequest
from django.core.files.base import ContentFile
from ajaxutils.decorators import ajax

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

    return {'data': response}


@ajax(require_POST=True)
@csrf_exempt
def story(request):
    """

    {
        name: "User Name",
        email: "user@example.com",
        posts: [
            {
                item_pk:  "item public key",
                image: "image/base64 image",
            },
        ]
    }
    """
    name = request.POST.get('fullname')
    email = request.POST.get('email')
    posts = json.loads(request.POST.get('posts', '[]'))

    if not all((name, email, posts)):
        return HttpResponseBadRequest()

    m = models.Museum.objects.latest('pk')
    t = models.Tour(name=name, email=email, museum=m)
    t.save()

    for i, post in enumerate(posts):
        item = post.get('item_pk')
        if item:
            item = get_object_or_404(models.Item, pk=item)

        image = post.get('image')
        if image:
            image=ContentFile(base64.decodestring(image))

        if not image and not item:
            return HttpResponseBadRequest()

        p = models.Post(ordering_index=i, tour=t, item=item, image=image)
        p.save()

    # fire up the notification system
    # TODO. fire using django's Signals, not directly.
    models.notify_email(sender='story_view', museum=m, tour=t)
    return {'status': 'completed'}
