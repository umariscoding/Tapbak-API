from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from loyalty.services.loyalty import LoyaltyService
import json

@api_view(["POST"])
def create_pass_view(request, vendorName):
    name = request.POST.get("name")
    email = request.POST.get("email")
    phone = request.POST.get("phone")
    vendor = vendorName
    data = {
        "customerDetails": {
            "name": name,
            "email": email,
            "phone": phone
        },
        "vendorDetails": {
            "name": vendor,
            "description": "Loyalty Card for " + vendor,
            "colors": {
                "background": "rgb(0,122,255)",
                "foreground": "rgb(255,255,255)",
                "label": "rgb(255,255,255)"
            },
            "logo": "https://picsum.photos/29/29",
            "stripImage": "https://picsum.photos/320/123",
            "backgroundImage": "https://picsum.photos/320/123"
        }
    }

    customerDetails = data.get(
        'customerDetails')
    vendorDetails = data.get('vendorDetails')

    loyaltyService = LoyaltyService(request)
    passData = loyaltyService.create_pass_json(
        customerDetails, vendorDetails)
    return HttpResponse(passData, content_type="application/vnd.apple.pkpass")