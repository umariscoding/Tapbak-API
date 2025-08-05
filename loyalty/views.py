from django.shortcuts import render
from django.http import HttpResponse
from django_walletpass.models import PassBuilder
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json


class CustomPassBuilder(PassBuilder):
    def pre_build_pass_data(self):
        """Override to not add authentication token and web service URL"""
        required_fields = {
            "passTypeIdentifier": self.pass_data_required.get("passTypeIdentifier"),
            "serialNumber": self.pass_data_required.get("serialNumber"),
            "teamIdentifier": self.pass_data_required.get("teamIdentifier"),
            "authenticationToken": "FHyKKnCDhUJENTLwaf",
            "webServiceURL": "https://3942d4f5abba.ngrok-free.app/pass"
        }
        self.pass_data.update(required_fields)


instance = PassBuilder()


# @api_view(["GET", "POST", "DELETE"])
# def update_pass_view(request, deviceLibraryIdentifier, passTypeIdentifier, serialNumber):
#     """
#     Handle Apple Wallet web service endpoints:
#     - GET: Get latest pass data
#     - POST: Register device for pass updates
#     - DELETE: Unregister device from pass updates
#     """
#     # Check authentication token (Apple Wallet sends this in Authorization header)
#     auth_header = request.headers.get('Authorization', '')
#     if not auth_header.startswith('ApplePushNotifications '):
#         return Response({'error': 'Invalid authentication'}, status=status.HTTP_401_UNAUTHORIZED)
    
#     if request.method == "GET":
#         # Return the latest pass data
#         # This should return the pass data in the same format as create_pass_view
#         return create_pass_view(request)
    
#     elif request.method == "POST":
#         # Register device for pass updates
#         # You might want to store this registration in your database
#         # For now, just return success
#         return Response(status=status.HTTP_201_CREATED)
    
#     elif request.method == "DELETE":
#         # Unregister device from pass updates
#         return Response(status=status.HTTP_200_OK)

@api_view(["GET"])
def create_pass_view(request):
    customer_id = "1234561237890"

    # Create an event ticket pass matching the provided JSON
    builder = CustomPassBuilder()
    builder.pass_data_required.update({
        "serialNumber": "ASDASDASD123123",
        "description": "Loyalty Card under my company tapback",
        "organizationName": "Tapbak",
        "passTypeIdentifier": "pass.co.tapback.loyalty",
        "teamIdentifier": "QK2FSS3243"
    })
    builder.pass_data.update({
        "formatVersion": 1,
        "passTypeIdentifier": "pass.co.tapback.loyalty",
        "serialNumber": "TEST123456",
        "teamIdentifier": "QK2FSS3243",
        "organizationName": "Tapbak",
        "description": "Loyalty Card under my company tapback",
        "logoText": "My Subhani Card",
        "foregroundColor": "rgb(255,255,255)",
        "backgroundColor": "rgb(0,122,255)",
        "labelColor": "rgb(255,255,255)",
        "barcode": {
            "message": "TEST123456",
            "format": "PKBarcodeFormatQR",
            "messageEncoding": "iso-8859-1"
        },
        "images": {
            "icon": "icon.png"
        },
        "secondary-auxiliary": [
            {
                "fieldUUID": "68149d00-71eb-11f0-82a6-7fc747b2be71",
                "value": "hello",
                "label": "world",
                "key": "HelloWorld"
            }
        ],
        "storeCard": {
            "primaryFields": [
                {
                    "key": "balance",
                    "label": "Points",
                    "value": "0"
                }
            ],
            "secondaryFields": [
                {
                    "key": "member",
                    "label": "Member Since",
                    "value": "2025-08-05"
                }
            ]
        }
    })
    file_content = open('certs/icon.png', 'rb').read()
    builder.add_file('icon.png', file_content)
    file_content = open('certs/logo.png', 'rb').read()
    builder.add_file('logo.png', file_content)
    pkpass_bytes = builder.build()
    pkpass_file = open("MyLoyaltyPass.pkpass", "wb")
    pkpass_file.write(pkpass_bytes)
    return HttpResponse(pkpass_bytes, content_type="application/vnd.apple.pkpass")
