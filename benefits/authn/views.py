from django.contrib.auth import authenticate, login
from django.http import HttpResponse


# https://docs.djangoproject.com/en/3.2/topics/auth/default/#how-to-log-a-user-in-1
def sign_in(request):
    user = authenticate(request)
    if user:
        login(request, user)
        response = HttpResponse("Signed in!")
    else:
        response = HttpResponse("Not signed in")

    return response


def check(request):
    if request.user.is_authenticated:
        response = HttpResponse("Signed in!")
    else:
        response = HttpResponse("Not signed in")

    return response
