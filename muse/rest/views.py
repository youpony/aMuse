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
import simplejson as json

from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from ajaxutils.decorators import ajax
from django.views.decorators.csrf import csrf_exempt

from muse.rest import models
from muse.rest.models import Museum, Tour, Item, Post


@ajax(require_GET=True)
def exhibitions_publiclist(request):
    """
    GET /api/m/
    """
    exhibitions = \
        models.Exhibition.objects.filter(
            end_date__gte=datetime.date.today()
        ).order_by('start_date').values(
            'title', 'description', 'pk'
        )
    return {'data': list(exhibitions)}


@ajax(require_GET=True)
def exhibition_details(request, pk):
    """
    GET /api/m/<pk>/
    Return all public informations about the selected exhibition.
    """
    exhibition = get_object_or_404(models.Exhibition, pk=pk)
    response = model_to_dict(
        exhibition,
        fields=('title', 'description')
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
    # response['exhibitions'] = [{'name': e.title, 'id': e.pk}
    #                            for e in item.exhibitions.all()]

    response['images'] = [
        request.build_absolute_uri(itemimage.image.url) for itemimage in
        models.ItemImage.objects.filter(item__pk=item.pk)
    ]

    return {'data': response}


@ajax(require_POST=True)
@csrf_exempt
def story(request):
    name = request.POST.get('fullname')
    email = request.POST.get('email')
    pks = json.loads(request.POST.get('listofpk'))

    t = Tour()
    t.public_id = hashlib.sha1(
        email + name + 'public'
    ).hexdigest()  # FIXME[mp]
    t.private_id = hashlib.sha1(email + name).hexdigest()  # FIXME[ml]
    t.name = name
    t.email = email
    t.museum = Museum.objects.all()[0]
    t.timestamp = datetime.datetime.now()

    t.save()

    for i, pk in enumerate(pks):
        p = Post()
        p.ordering_index = i
        p.tour = t
        p.item = Item.objects.get(pk=pk)

        p.save()

    return {
        'status': 'completed',
        'exit_status': 200
    }
