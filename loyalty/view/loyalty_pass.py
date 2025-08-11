from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from loyalty.services.loyalty import LoyaltyService
from loyalty.models import Vendor, PassTemplate, TemplateField, Customer, LoyaltyCard


@api_view(["POST"])
def create_pass_view(request, vendorId):
    vendor = Vendor.objects.get(id=vendorId)
    customer = create_customer(request.POST.get("firstName"), request.POST.get(
        "lastName"), request.POST.get("email"), request.POST.get("contactNumber"), vendor)
    passTemplate = PassTemplate.objects.get(vendor=vendor)
    templateFields = TemplateField.objects.filter(pass_template=passTemplate)
    headerField = templateFields.filter(field_type="header")[0]
    secondaryFields = templateFields.filter(field_type="secondary")

    context = {
        "customer": customer,
        "vendor": vendor,
        "headerField": headerField,
        "secondaryFields": secondaryFields,
        "passTemplate": passTemplate
    }
    
    loyaltyService = LoyaltyService(request, context)
    passData, metadata = loyaltyService.create_pass_json()
    loyaltyService.builder.write_to_model()
    loyalty_card = create_loyalty_card_in_database(request, metadata)
    customer.loyalty_card = loyalty_card
    customer.save()
    return HttpResponse(passData, content_type="application/vnd.apple.pkpass")


def create_customer(firstName, lastName, email, phone, vendor):
    customer = Customer.objects.create(
        first_name=firstName,
        last_name=lastName,
        email=email,
        contact_number=phone,
        vendor=vendor
    )
    return customer


def create_loyalty_card_in_database(request, metadata):
    LoyaltyCard.objects.create(
        loyalty_points=0,
        authentication_token=metadata["authenticationToken"],
        web_service_url="https://9674bf5a250a.ngrok-free.app/pass",
        serial_number=metadata["serialNumber"],
        meta_data=metadata['loyalty_metadata']
    )
