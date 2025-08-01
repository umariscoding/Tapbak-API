from django.shortcuts import render
from django.http import HttpResponse
from django_walletpass.models import PassBuilder
from rest_framework.decorators import api_view
import json

instance = PassBuilder()

@api_view(["POST"])
def create_pass_view(request):
    # Handle both JSON and form data
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    
    print("Received data:", data)
    
    customer_id = data.get("customer_id")
    if customer_id:
        background_color = data.get("backgroundColor")
        foreground_color = data.get("foregroundColor")
        label_color = data.get("labelColor")
        name = data.get("name")
        member_level = data.get("memberLevel")
        next_appointment = data.get("nextAppointment")
        points = data.get("points")
        tier_progress = data.get("tierProgress")
        expires = data.get("expires")
        noOfAwards = data.get("noOfAwards")
        membership_id = data.get("membershipId")
        rewards_details = data.get("rewardsDetails")
        support = data.get("support")
        terms = data.get("terms")
        locations = data.get("locations")
        relevant_date = data.get("relevantDate")
    
    # Create a simple pass for now
    builder = PassBuilder()
    builder.pass_data_required.update({
        "serialNumber": f"customer-{customer_id or '123'}",
        "description": "Loyalty Card",
        "organizationName": "TapBak",
    })

    builder.pass_data.update({
        # Colors
        "backgroundColor": background_color or "rgb(60, 65, 76)",
        "foregroundColor": foreground_color or "rgb(255, 255, 255)",
        "labelColor": label_color or "rgb(255, 255, 255)",
        
        # Barcode
        "barcode": {
            "message": membership_id or "123456789",
            "format": "PKBarcodeFormatPDF417",
            "messageEncoding": "iso-8859-1"
        },
        
        # Store Card Pass Type with Text Fields
        "storeCard": {
            "primaryFields": [{
                "key": "awards",
                "label": "Awards",
                "value": noOfAwards or "$50.00", 
                "textAlignment": "PKTextAlignmentCenter"
            }],
            
            "secondaryFields": [{
                "key": "member_level",
                "label": "Member Level",
                "value": member_level or "Gold",
                "textAlignment": "PKTextAlignmentLeft"
            }, {
                "key": "points",
                "label": "Points",
                "value": points or "1,250",
                "textAlignment": "PKTextAlignmentRight"
            }],
            
            "auxiliaryFields": [{
                "key": "expires",
                "label": "Expires",
                "value": expires or "2024-12-31",
                "textAlignment": "PKTextAlignmentCenter"
            }],
            
            "headerFields": [{
                "key": "name",
                "label": "NAME",
                "value": name or "TapBak",
                "textAlignment": "PKTextAlignmentCenter"
            }],
            
            "backFields": [{
                "key": "terms",
                "label": "Terms & Conditions",
                "value": terms or "Valid at participating locations. Cannot be combined with other offers.",
                "textAlignment": "PKTextAlignmentJustified"
            }, {
                "key": "support",
                "label": "Support",
                "value": support or "support@tapbak.com",
                "textAlignment": "PKTextAlignmentLeft"
            }]
        }
    })
    
    pkpass_bytes = builder.build()
    pkpass_file = open("mypass.pkpass", "wb")
    pkpass_file.write(pkpass_bytes)
    return HttpResponse(pkpass_bytes, content_type="application/vnd.apple.pkpass")
