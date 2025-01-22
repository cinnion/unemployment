from typing import List, Union

from django.urls import path, URLResolver, URLPattern
from . import views

app_name = 'applications'

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('', views.applications_list, name='application-list'),
    path('<int:appid>/edit', views.application_details, name='application-details'),
    path('new-host/', views.application_details, name='new-application'),
]
