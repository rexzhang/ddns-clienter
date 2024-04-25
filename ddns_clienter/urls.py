"""ddns_clienter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

import django_eventstream
from django.urls import include, path

from ddns_clienter_core.views import views
from ddns_clienter_core.views.api import api

urlpatterns = [
    path("api/", api.urls),
    path("sse/status", include(django_eventstream.urls), {"channels": ["status"]}),
    path("", views.HomePageView.as_view(), name="home_page"),
    path(
        "trouble_shooting",
        views.TroubleShootingView.as_view(),
        name="trouble_shooting",
    ),
    # path("sse/status", views.status_sse),
]
