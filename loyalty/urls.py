from django.urls import path
from . import views

urlpatterns = [
    path("create", views.create_pass_view, name="create-pass"),
    path("download", views.download_pass_view, name="download-pass"),
    path("test", views.test_page_view, name="test-page"),
]