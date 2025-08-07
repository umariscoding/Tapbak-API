from django.urls import path 
from loyalty.view.loyalty_pass import create_pass_view
from loyalty.view.vendor import create_vendor_view
urlpatterns = [
    path("create/<str:vendorName>", create_pass_view, name="create_pass"),
    path("create-vendor", create_vendor_view, name="create_vendor")
]