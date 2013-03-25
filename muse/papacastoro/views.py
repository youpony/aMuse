from django.shortcuts import render
from muse.rest.models import Tour


def tour(request, public_id):
    t = Tour.objects.get(public_id=public_id)
    return render(request, 'papacastoro/index.html', {'tour': t})

