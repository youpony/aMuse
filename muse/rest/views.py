"""
API in json
 - tutte le mostre  GET /m/
 x creare mostra POST /m/
 - dettagli mostra  GET /m/<id>/
 x edit mostra  PUT /m/<id>/
 x remove mostra  DELETE /m/<id>/ piuttosto data inizio e data fine...
 - tutti gli oggetti di una data mostra  GET /m/<id>/o/
 x creare oggetto POST /o/
 - dettagli oggetto  GET /o/<id>/
 x edit oggetto  PUT /o/<id>/
 - inviare i preferiti segnati POST /s/
 - link pubblico visualizzazione story GET /s/<numero_casuale>/
 - link per edit storytelling PUT /s/<numero_casuale>/

"""
from functools import wraps
import datetime

import simplejson as json
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from ajaxutils.views import View, AjaxMixin
from ajaxutils.decorators import ajax

from muse.rest import models


@ajax(require_GET=True)
def exhibitions_publiclist(request):
    """
    GET /api/m/
    """
    exhibitions = models.Exhibition.objects.filter(
             end_date__gte=datetime.date.today(),
             ).order_by('start_date'
             ).values('title', 'description')
    return {'data': list(exhibitions)}


@ajax(require_GET=True)
def exhibition_detail(request, pk):
    """
    GET /api/m/<pk>/
    Return all public informations about the selected exhibition.
    """
    raise NotImplementedError

@ajax(require_GET=True)
def exhibition_items(request, pk):
    """
    GET /api/m/<pk>/o/
    Return a list of available objects
    """
    e = get_object_or_404(models.Exhibition, pk=pk)
    items = models.Item.objects.filter(exhibitions__pk__contains=pk
            ).order_by('name').values('name', 'desc', 'year', 'author')

    return {'data': list(items)}


@ajax(require_GET=True)
def item_detail(request):
    """
    GET /o/<pk>
    Return a list of available items.
    """
    raise NotImplementedError

