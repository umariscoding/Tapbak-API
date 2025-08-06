from django.urls import path 
from loyalty.views import *
urlpatterns = [
    path("create/<str:vendorName>", create_pass_view, name="create_pass")
]