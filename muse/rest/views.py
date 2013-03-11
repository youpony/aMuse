from functools import wraps
import datetime

import simplejson as json
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse

from muse.rest import models


def exhibitions_list(request):
    """
    GET /api/m/
    returns a list of the last ten exhibitions.
    """
    exhibitions = models.Exhibition.objects.filter(
             end_date__gte=datetime.date.today(),
             ).order_by('start_date'
             ).values('title', 'description')
    return HttpResponse(json.dumps({'data': list(exhibitions)}))
