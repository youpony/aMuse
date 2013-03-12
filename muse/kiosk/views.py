from django.shortcuts import render


def home(request):
    return render(request, 'kiosk/index.html', {})


def objects(request, pk=1):
    return render(request, 'kiosk/objects.html', {'pk': pk})
