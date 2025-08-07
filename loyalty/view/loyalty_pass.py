from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from loyalty.services.loyalty import LoyaltyService
from loyalty.models import Vendor

@api_view(["POST"])
def create_pass_view(request, vendorName):

    data = {

    }
    name = request.POST.get("firstName") + " " + request.POST.get("lastName")
    email = request.POST.get("email")
    phone = request.POST.get("contactNumber")
    vendor = Vendor.objects.get(id = "e2da609d8d6b4fdd8a4e65fe7b55ce62")
    template = {
        "id": "e2da609d8d6b4fdd8a4e65fe7b55c232",
        "vendor": vendor.id, 
        "headerFields" : [
            {}

        ]
    }
    customerDetails = data.get(
        'customerDetails')
    vendorDetails = data.get('vendorDetails')

    loyaltyService = LoyaltyService(request)
    passData = loyaltyService.create_pass_json(
        customerDetails, vendorDetails)
    return HttpResponse(passData, content_type="application/vnd.apple.pkpass")
 