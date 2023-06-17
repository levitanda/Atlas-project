"""
URL configuration for RAICAT project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from cra_helper.views import proxy_cra_requests
from django.views.generic import TemplateView
from .views import dns_data

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(
        r"^dns_data/first_date=(?P<first_date>\d{4}-\d{2}-\d{2})&second_date=(?P<second_date>\d{4}-\d{2}-\d{2})/$",
        dns_data,
        name="dns_data",
    ),
    path("raicat/", TemplateView.as_view(template_name="entry_point.html")),
]
if settings.DEBUG:
    proxy_urls = [
        re_path(r"^__webpack_dev_server__/(?P<path>.*)$", proxy_cra_requests),
        re_path(
            r"^(?P<path>.+\.hot-update\.(js|json|js\.map))$",
            proxy_cra_requests,
        ),
    ]
    urlpatterns.extend(proxy_urls)
