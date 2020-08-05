from django.urls import path

from . import views

app_name = 'eligibility'
urlpatterns = [
    # /eligiblity
    path('', views.index, name='index'),
    # /eligibility/verify
    path('verify', views.verify, name='verify'),
    # /eligibility/verify/verified
    path('verify/verified', views.verified, name='verified'),
    # /eligibility/verify/unverified
    path('verify/unverified', views.unverified, name='unverified')
]
