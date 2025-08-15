from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os
from django.http import HttpResponse
from django_walletpass.models import Pass
from loyalty.services.loyalty import LoyaltyService
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
    # Check for duplicate Pass before saving
    pass_type_identifier = loyaltyService.builder.pass_data_required["passTypeIdentifier"]
    serial_number = metadata["serialNumber"]
    if Pass.objects.filter(pass_type_identifier=pass_type_identifier, serial_number=serial_number).exists():
        return Response({"error": "A pass with this passTypeIdentifier and serialNumber already exists."}, status=status.HTTP_400_BAD_REQUEST)
    loyaltyService.builder.write_to_model()
    loyalty_card = create_loyalty_card_in_database(request, metadata)
    customer.loyalty_card = loyalty_card
    customer.save()
    return HttpResponse(passData, content_type="application/vnd.apple.pkpass")


def create_customer(firstName, lastName, email, phone, vendor, dateOfBirth):
    customer = Customer.objects.create(
        first_name=firstName,
        last_name=lastName,
        email=email,
        contact_number=phone,
        vendor=vendor,
        date_of_birth=dateOfBirth
    )
    return customer


def create_loyalty_card_in_database(request, metadata):
    return LoyaltyCard.objects.create(
        loyalty_points=0,
        authentication_token=metadata["authenticationToken"],
        web_service_url=os.getenv("WEB_SERVICE_URL"),
        serial_number=metadata["serialNumber"],
        meta_data=metadata['loyalty_metadata']
    )

def ping_apple_wallet(serial_number):
    from django.conf import settings
    import os
    print("WALLETPASS_CONF:", getattr(settings, "WALLETPASS_CONF", None))
    key_path = getattr(settings, "WALLETPASS_CONF", {}).get("TOKEN_AUTH_KEY_PATH")
    print("TOKEN_AUTH_KEY_PATH:", key_path)
    print("Key exists:", os.path.exists(key_path) if key_path else "No key path")
    pass_obj = Pass.objects.get(serial_number=serial_number)
    pass_obj.push_notification()
    return True