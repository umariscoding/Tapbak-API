from django.urls import path 
from loyalty.view.loyalty_pass import create_pass_view
from loyalty.view.vendor import create_vendor_view
from loyalty.view.wallet import register_device, log_message, get_updated_pass, serve_updated_pass
from loyalty.view.auth import CookieTokenRefreshView
from loyalty.view.vendor import login_view, get_statistics
from loyalty.view.vendor import save_vendor_config, get_vendor_config
from loyalty.view.field_definition import get_field_definitions
from loyalty.view.vendor import get_customers, update_customer_status, update_vendor, get_public_vendor, upload_image, fetch_customer, process_transaction
from loyalty.view.vendor import get_transactions
urlpatterns = [

    # Authentication endpoints
    # Vendor endpoints
    path("create-vendor", create_vendor_view, name="create_vendor"),
    path("login", login_view, name="login"),
    path("statistics", get_statistics, name="get_statistics"),
    path("save-config", save_vendor_config, name="save_vendor_config"),
    path("config", get_vendor_config, name="get_vendor_config"),
    path("field-definitions", get_field_definitions, name="get_field_definitions"), 
    path("customers", get_customers, name="get_customers"),
    path("customers/<str:customer_id>/status", update_customer_status, name="update_customer_status"),
    path("vendor", update_vendor, name="update_vendor"),
    path("public-vendor/<str:vendor_id>", get_public_vendor, name="get_public_vendor"),
    path("upload-image", upload_image, name="upload_image"),
    path("customers/<str:customer_id>", fetch_customer, name="fetch_customer"),
    path("process-transaction", process_transaction, name="process_transaction"),
    # Pass endpoints
    path("create/<str:vendorId>", create_pass_view, name="create_pass"),
    path("transactions", get_transactions, name="get_transactions"),
    # Apple Wallet Pass endpoints
    path("v1/devices/<str:device_library_id>/registrations/<str:pass_type_id>/<str:serial_number>", register_device, name="device_registration"),
    path("v1/devices/<str:device_library_id>/registrations/<str:pass_type_id>", get_updated_pass, name="get_updated_pass"),
    path("v1/passes/<str:pass_type_id>/<str:serial_number>", serve_updated_pass, name="serve_updated_pass"),
    path("v1/log", log_message, name="log_message"),

    # Token refresh endpoint
    path("token/refresh", CookieTokenRefreshView.as_view(), name="token_refresh"),

]