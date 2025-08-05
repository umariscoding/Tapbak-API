from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from loyalty.services.loyalty import LoyaltyService


@api_view(["GET"])
def create_pass_view(request):
    data = {
        "customerDetails": {
            "name": "Subhan Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890"
        },
        "vendorDetails": {
            "name": "Tapbak Coffee Shop",
            "description": "Loyalty Card for Tapbak Coffee Shop",
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