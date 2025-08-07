from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from loyalty.services.loyalty import LoyaltyService
from loyalty.models import Vendor, PassTemplate, TemplateField, Customer

@api_view(["POST"])
def create_pass_view(request, vendorId):
    customer = create_customer(request.POST.get("firstName"), request.POST.get("lastName"), request.POST.get("email"), request.POST.get("contactNumber"))
    vendor = Vendor.objects.get(id = vendorId)
    passTemplate = PassTemplate.objects.get(vendor = vendor)
    templateFields = TemplateField.objects.filter(pass_template = passTemplate)
    headerField = templateFields.filter(field_type = "header")[0]
    secondaryFields = templateFields.filter(field_type = "secondary")

    
    loyaltyService = LoyaltyService(request)
    context = {
        "customerDetails": customer,
        "vendor":vendor,
        "headerField":headerField,
        "secondaryFields":secondaryFields,
        "passTemplate":passTemplate
    }
    passData = loyaltyService.create_pass_json(context)
    return HttpResponse(passData, content_type="application/vnd.apple.pkpass")
 

def create_customer(firstName, lastName, email, phone):
    customer = Customer.objects.create(
        first_name = firstName,
        last_name = lastName,
        email = email,
        phone = phone
    )
    return customer