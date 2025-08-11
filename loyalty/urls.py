from django.urls import path 
from loyalty.view.loyalty_pass import create_pass_view
from loyalty.view.vendor import create_vendor_view
from loyalty.view.field_definition import get_field_definitions
from loyalty.view.wallet import register_device, log_message, get_updated_pass, serve_updated_pass

urlpatterns = [
    path("create/<str:vendorId>", create_pass_view, name="create_pass"),
    path("create-vendor", create_vendor_view, name="create_vendor"),
    path("field-definitions", get_field_definitions, name="get_field_definitions"),

    # Apple Wallet Pass endpoints
    # Single endpoint for both register (POST) and unregister (DELETE) operations
    path("v1/devices/<str:device_library_id>/registrations/<str:pass_type_id>/<str:serial_number>", register_device, name="device_registration"),
    path("v1/devices/<str:device_library_id>/registrations/<str:pass_type_id>", get_updated_pass, name="get_updated_pass"),
    path("v1/passes/<str:pass_type_id>/<str:serial_number>", serve_updated_pass, name="serve_updated_pass"),
    path("v1/log", log_message, name="log_message"),
]