from django.shortcuts import render

from ddns_clienter import __name__ as name, __version__, __project_url__


def index_view(request):
    context = {
        "name": name,
        "version": __version__,
        "project_url": __project_url__,
    }
    return render(request, "index.html", context)
