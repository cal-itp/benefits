"""
eligibility_verification URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path


handler400 = "eligibility_verification.core.views.bad_request"
handler404 = "eligibility_verification.core.views.page_not_found"
handler500 = "eligibility_verification.core.views.server_error"

urlpatterns = [
    path("", include("eligibility_verification.core.urls")),
    path("eligibility/", include("eligibility_verification.eligibility.urls")),
    path("admin/", admin.site.urls)
]
