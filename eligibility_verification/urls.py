"""
eligibility_verification URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("", include("eligibility_verification.core.urls")),
    path("eligibility/", include("eligibility_verification.eligibility.urls")),
    path("admin/", admin.site.urls)
]
