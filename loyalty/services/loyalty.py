import uuid
import os
from datetime import datetime
from django_walletpass.models import PassBuilder
import requests

class LoyaltyService:
    def __init__(self, request):
        self.request = request
        self.builder = PassBuilder()

    def create_pass_json(self, customerDetails, vendorDetails):
        metadata = self.create_metadata(customerDetails, vendorDetails)

        self.builder.pass_data_required.update({
            "passTypeIdentifier": os.getenv("PASS_TYPE_ID"),
            "teamIdentifier": os.getenv("TEAM_ID"),
            "organizationName": os.getenv("ORGANIZATION_NAME"),
            "serialNumber": metadata["serialNumber"],
            "webServiceURL":"https://3942d4f5abba.ngrok-free.app/pass/v1",
            "authenticationToken": metadata["authenticationToken"],
            "description": metadata["description"],
        })

        self.builder.pass_data.update({
            "formatVersion": 1,
            "backgroundColor": metadata["colors"]["background"],
            "foregroundColor": metadata["colors"]["foreground"],
            "labelColor": metadata["colors"]["label"],
            "images": {
                "logo": "logo.png",
                "icon": "icon.png",
                "stripImage": "strip.png",
            },

            "logoText": metadata["vendorDetails"]["name"],
            "barcode": {
                "message": metadata["customerId"],
                "format": "PKBarcodeFormatQR",
                "messageEncoding": "iso-8859-1",
            },
            "storeCard": {
                "headerFields": [
                    {
                        "key": "Points",
                        "label": "Points",
                        "value": metadata["loyaltyPoints"]
                    }
                ],
                "secondaryFields": [
                    {
                        "key": "Name",
                        "label": "Name",
                        "value": metadata["customerDetails"]["name"]
                    },
                    {
                        "key": "Member Since",
                        "label": "Member Since",
                        "value": datetime.now().strftime("%Y-%m-%d")
                    }
                ]
            }
        })

        try: 
            if metadata["images"]["stripImage"]:
                strip_response = requests.get(metadata["images"]["stripImage"])
                if strip_response.status_code == 200:
                    self.builder.add_file("strip.png", strip_response.content)
                else:
                    print(f"Warning: Failed to fetch strip image from {metadata['images']['stripImage']}")
        except Exception as e:
            print(f"Warning: Could not add strip image: {e}")
        try:
            if metadata["images"]["logo"]:
                logo_response = requests.get(metadata["images"]["logo"])
                if logo_response.status_code == 200:
                    self.builder.add_file("logo.png", logo_response.content)
                else:
                    print(f"Warning: Failed to fetch logo from {metadata['images']['logo']}")
         
        except Exception as e:
            print(f"Warning: Could not add logo image: {e}")
            print(metadata["images"]["logo"])

        try:
            if metadata["images"]["icon"]:
                icon_response = requests.get(metadata["images"]["icon"])
                if icon_response.status_code == 200:
                    self.builder.add_file("icon.png", icon_response.content)
                else:
                    print(f"Warning: Failed to fetch icon from {metadata['images']['icon']}")
        except Exception as e:
            print(f"Warning: Could not add icon image: {e}")
           
        
        return self.builder.build()

    def create_metadata(self, customerDetails, vendorDetails):
        customerId = str(uuid.uuid4())
        authenticationToken = str(uuid.uuid4())
        webServiceURL = "https://3942d4f5abba.ngrok-free.app/pass/v1"
        teamID = os.getenv("TEAM_ID")
        passTypeIdentifier = os.getenv("PASS_TYPE_ID")
        organizationName = os.getenv("ORGANIZATION_NAME")
        serialNumber = customerId
        description = vendorDetails["description"]
        colors = vendorDetails["colors"]
        loyaltyPoints = 0
        images = {
            "logo": vendorDetails["logo"],
            "icon": vendorDetails["logo"],
            "stripImage": vendorDetails["stripImage"],
            "backgroundImage": vendorDetails["backgroundImage"],
        }

        return {
            "customerId": customerId,
            "authenticationToken": authenticationToken,
            "webServiceURL": webServiceURL,
            "teamID": teamID,
            "passTypeIdentifier": passTypeIdentifier,
            "organizationName": organizationName,
            "serialNumber": serialNumber,
            "description": description,
            "colors": colors,
            "loyaltyPoints": loyaltyPoints,
            "images": images,
            "customerDetails": customerDetails,
            "vendorDetails": vendorDetails,
        }
