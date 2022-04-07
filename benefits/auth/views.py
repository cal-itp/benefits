from django.http import JsonResponse
from benefits.core import session


def login(request):
    # TODO THIS IS NOT PROPER AUTHENTICATION. Just implemented this way for testing.
    session.update(request, auth=True)
    return JsonResponse(session.context_dict(request))
