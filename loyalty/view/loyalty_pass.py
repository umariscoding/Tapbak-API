from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os
from django.http import HttpResponse
from django_walletpass.models import Pass
from loyalty.services.loyalty import LoyaltyService, create_customer, create_loyalty_card_in_database, ping_apple_wallet
from loyalty.models import Vendor, PassTemplate, TemplateField, Customer, LoyaltyCard, Reward


@api_view(["POST"])
def create_pass_view(request, vendorId):
    vendor = Vendor.objects.get(id=vendorId)
    customer = create_customer(request.POST.get("firstName"), request.POST.get(
        "lastName"), request.POST.get("email"), request.POST.get("contactNumber"), vendor, request.POST.get("dateOfBirth"))
    passTemplate = PassTemplate.objects.get(vendor=vendor)
    templateFields = TemplateField.objects.filter(pass_template=passTemplate)
    headerField = templateFields.filter(field_type="header")[0]
    secondaryFields = templateFields.filter(field_type="secondary")
    noOfRewards = Reward.objects.filter(customer=customer, status="available").count()
    context = {
        "customer": customer,
        "vendor": vendor,
        "headerField": headerField,
        "secondaryFields": secondaryFields,
        "passTemplate": passTemplate,
        "noOfRewards": noOfRewards
    }
    
    loyaltyService = LoyaltyService(request, context)

    passData, metadata = loyaltyService.create_pass_json()

    pass_type_identifier = loyaltyService.builder.pass_data_required["passTypeIdentifier"]
    serial_number = metadata["serialNumber"]
    if Pass.objects.filter(pass_type_identifier=pass_type_identifier, serial_number=serial_number).exists():
        return Response({"error": "A pass with this passTypeIdentifier and serialNumber already exists."}, status=status.HTTP_400_BAD_REQUEST)
    
    loyaltyService.builder.write_to_model()
    loyalty_card = create_loyalty_card_in_database(request, metadata)
    customer.loyalty_card = loyalty_card
    customer.save()
    return HttpResponse(passData, content_type="application/vnd.apple.pkpass")