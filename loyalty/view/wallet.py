from rest_framework.decorators import api_view
from django_walletpass.classviews import RegisterPassViewSet
from rest_framework.response import Response
from rest_framework import status
from loyalty.models import Vendor, PassTemplate, TemplateField, LoyaltyCard, Customer, Reward
from loyalty.services.loyalty import LoyaltyService
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
import json
from datetime import datetime

@api_view(["POST", "DELETE"])
def register_device(request, device_library_id, pass_type_id, serial_number): 
    try:
        view = RegisterPassViewSet() 
        if request.method == "POST":
            view.create(request, device_library_id, pass_type_id, serial_number)
            print("Device registered")
            return Response(status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            view.delete(request, device_library_id, pass_type_id, serial_number)
            print("Device deleted")
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        print(f"Error registering device: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def get_updated_pass(request, device_library_id, pass_type_id):
    try:
        passes_updated_since = request.GET.get("passesUpdatedSince")
        from datetime import datetime
        from loyalty.models import LoyaltyCard
        if passes_updated_since:
            try:
                passes_updated_since = datetime.fromisoformat(passes_updated_since)
            except Exception:
                # fallback for Zulu time (strip Z)
                passes_updated_since = datetime.fromisoformat(passes_updated_since.rstrip("Z"))
        else:
            passes_updated_since = datetime.min

        updated_cards = LoyaltyCard.objects.all()

        serial_numbers = list(updated_cards.values_list("serial_number", flat=True))
        last_updated = updated_cards.order_by("-updated_at").first().updated_at if updated_cards else datetime.now()

        response_data = {
            "serialNumbers": serial_numbers,
            "lastUpdated": last_updated.isoformat() if last_updated else datetime.now().isoformat()
        }
        return JsonResponse(response_data, content_type="application/json")
    except Exception as e:
        print(f"Error getting updated pass: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def serve_updated_pass(request, pass_type_id, serial_number):
    try:
        loyalty_pass = get_object_or_404(LoyaltyCard, serial_number=serial_number)
        customer = get_object_or_404(Customer, loyalty_card=loyalty_pass)
        vendor = get_object_or_404(Vendor, id=customer.vendor.id)
        passTemplate = get_object_or_404(PassTemplate, vendor=vendor)
        templateFields = TemplateField.objects.filter(pass_template=passTemplate)
        
        headerField = templateFields.filter(field_type="header").first()
        
        noOfRewards = Reward.objects.filter(customer=customer, status="available").count()
        secondaryFields = templateFields.filter(field_type="secondary")
        
        context = {
            "customer": customer,
            "vendor": vendor,
            "headerField": headerField,
            "secondaryFields": secondaryFields,
            "passTemplate": passTemplate,
            "noOfRewards": noOfRewards
        }
        
        loyaltyService = LoyaltyService(request, context)
        passData, metadata = loyaltyService.create_pass_json(
            serialNumber=serial_number, 
            authenticationToken=loyalty_pass.authentication_token
        )

        return HttpResponse(passData, content_type="application/vnd.apple.pkpass")
    except Exception as e:
        print(f"Error serving updated pass: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def log_message(request):
    try:
        print("Log message received:", request.data)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error processing log message: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

