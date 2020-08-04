"""
eligibility_verification URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path


urlpatterns = [
    path("admin/", admin.site.urls)
]
