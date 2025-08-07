import uuid
import os
from datetime import datetime
from django_walletpass.models import PassBuilder
import requests

class LoyaltyService:
    def __init__(self, request, context):
        self.request = request
        self.context = context
        self.builder = PassBuilder()

    def create_pass_json(self, context):
        metadata = self.create_metadata(context)

        self.builder.pass_data_required.update({
            "passTypeIdentifier": os.getenv("PASS_TYPE_ID"),
            "teamIdentifier": os.getenv("TEAM_ID"),
            "organizationName": os.getenv("ORGANIZATION_NAME"),
            "serialNumber": metadata["serialNumber"],
            "webServiceURL":"https://3942d4f5abba.ngrok-free.app/pass/v1",
            "authenticationToken": metadata["authenticationToken"],
            "description": metadata["description"],
        })

        secondaryFields = [] 
        for field in context["secondaryFields"]:
            secondaryFields.append({
                "key": field.name,
                "value": 0,
                "changeMessage": "0"
            })

        self.builder.data.update({
            "formatVersion": 1, 
            "logoText": context["vendor"].business_name,
            "barcode": {
                "message": context["customer"].id,
                "format": "PKBarcodeFormatQR",
                "messageEncoding": "iso-8859-1"
            },
            "headerFields": context["headerFields"],
            "secondaryFields": secondaryFields
        })

        return self.builder.build()

    def get_value(self, formDefinition):
        match (formDefinition.name.lower()):
            case "Name":
                return self.context["customer"].first_name + " " + self.context["customer"].last_name 
            case "date of birth":
                return self.context["customer"].date_of_birth.strftime("%Y-%m-%d")
            case "email":
                return self.context["customer"].email
            case "phone":
                return self.context["customer"].phone
            case "loyalty points":
                return 0
            case "rewards":
                return 0
            case _:
                return ""