"""
The core application: view definition for the root of the webapp.
"""
from django.shortcuts import render


def index(request):
    return render(request, "core/index.html")
