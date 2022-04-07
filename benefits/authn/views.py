from django.contrib.auth import authenticate, login
from django.http import HttpResponse


def sign_in(request):
    user = authenticate(request)
    if user:
        login(request, user)
        response = HttpResponse("Signed in!")
    else:
        response = HttpResponse("Not signed in")

    return response
