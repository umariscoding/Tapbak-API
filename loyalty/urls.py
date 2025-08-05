from django.urls import path
from . import views

urlpatterns = [
    path("create", views.create_pass_view, name="create-pass"),
    # path("v1/devices/<str:deviceLibraryIdentifier>/registrations/<str:passTypeIdentifier>/<str:serialNumber>", views.update_pass_view, name="update-pass"),
    # path("v1/passes/<str:passTypeIdentifier>/<str:serialNumber>", views.update_pass_view, name="update-pass"),
]