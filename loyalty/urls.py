from django.urls import path 
from loyalty.view.loyalty_pass import create_pass_view
from loyalty.view.vendor import create_vendor_view
from loyalty.view.field_definition import get_field_definitions
urlpatterns = [
    path("create/<str:vendorId>", create_pass_view, name="create_pass"),
    path("create-vendor", create_vendor_view, name="create_vendor"),
    path("field-definitions", get_field_definitions, name="get_field_definitions")
]