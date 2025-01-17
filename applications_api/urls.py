from typing import List, Union

from django.urls import path,  URLResolver, URLPattern

from applications_api.views import JobApplications, JobApplicationDetail

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path("", JobApplications.as_view()),
    path("<int:pk>", JobApplicationDetail.as_view())
]
