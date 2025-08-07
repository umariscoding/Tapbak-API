from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from loyalty.models import Vendor

@api_view(["POST"])
def create_vendor_view(request):
    vendor = Vendor.objects.create(
        businessName = "Ahmed Gul",
        businessDescription = "Ahmed Gul's Business",
        email = "ahmedgul@gmail.com",
        password = "123456",
    )
    return Response(status=status.HTTP_201_CREATED)