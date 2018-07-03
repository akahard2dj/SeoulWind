from django.http import HttpRequest
from django.http import HttpResponse
from django.template import loader


def index(request: HttpRequest):
    template = loader.get_template('windows/index.html')
    return HttpResponse(template.render())
