from django.http import HttpResponse
from django_walletpass.models import PassBuilder
from rest_framework.decorators import api_view

@api_view(["GET"])
def create_pass_view(request):
    builder = PassBuilder()
    builder.pass_data_required.update({
        "passTypeIdentifier": "pass.co.tapback.loyalty",
        "serialNumber": "TEST123456",
        "teamIdentifier": "QK2FSS3243",
        "authenticationToken": "FHyKKnCDhUJENTLwaf",
        "webServiceURL": "https://3942d4f5abba.ngrok-free.app/pass"
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
