from django.shortcuts import render
from ajaxutils.decorators import ajax


def home(request):
    return render(request, 'kiosk/index.html', {})


@ajax()
def get(request):
    return {
        'data': [{'title':'bla'}, {'title': 'bla2'}]
    }