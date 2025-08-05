from django.shortcuts import render
from django.http import HttpResponse
from django_walletpass.models import PassBuilder
from rest_framework.decorators import api_view
import json

instance = PassBuilder()

@api_view(["GET"])
def create_pass_view(request):
    customer_id = "1234561237890"
    if customer_id:
        background_color = "rgb(21, 21, 21)"
        foreground_color = "rgb(255, 255, 255)"
        label_color = "rgb(255, 255, 255)"
        locations = [{
            "longitude": 12.345678,
            "latitude": 12.345678,
            "relevantText": "You're near my home."
        }]
        relevant_date = "2021-08-28T00:00-18:00"
    
    # Create an event ticket pass matching the provided JSON
    builder = PassBuilder()
    builder.pass_data_required.update({
        "serialNumber": f"event-{customer_id or 'nmyuxofgna'}",
        "description": "Event Ticket",
        "organizationName": "Tapbak",
        "passTypeIdentifier": "pass.co.tapback.loyalty",
        "teamIdentifier": "QK2FSS3243"
    })

    builder.pass_data.update({
        
        "backgroundColor": background_color or "rgb(21, 21, 21)",
        "foregroundColor": foreground_color or "rgb(255, 255, 255)",
        "labelColor": label_color or "rgb(255, 255, 255)",
        "icon": "icon.png",
        "logoText": "Tapbak",
        "logoImage": "logo.png",
        "storeCard": {
            "headerFields": [{
                "label": "MEMBERSHIP ID",
                "key": "membershipId",
                "value": "1234567890"
            }],
            
            "secondaryFields": [{
                "key": "name",
                "label": "NAME",
                "value": "John Doe"
            }],
            
            "auxiliaryFields": [{
                "key": "memberLevel",
                "label": "MEMBER LEVEL",
                "value": "Gold"
            }],
            
            "backFields": [{
                "key": "nextAppointment",
                "label": "NEXT APPOINTMENT",
                "value": "2021-08-28T00:00-18:00"
            }]
        },
        
        # Location (if provided)
        "locations": locations or [{
            "longitude": 12.345678,
            "latitude": 12.345678,
            "relevantText": "You're near my home."
        }],
        
        # Relevant date
        "relevantDate": relevant_date or "2021-08-28T00:00-18:00"
    })
    
    file_content = open('certs/icon.png', 'rb').read()
    builder.add_file('icon.png', file_content)
    file_content = open('certs/logo.png', 'rb').read()
    builder.add_file('logo.png', file_content)
    pkpass_bytes = builder.build()
    pkpass_file = open("MyLoyaltyPass.pkpass", "wb")
    pkpass_file.write(pkpass_bytes)
    return HttpResponse(pkpass_bytes, content_type="application/vnd.apple.pkpass")

@api_view(["GET"])
def download_pass_view(request):
    """Serve the generated pass file directly for testing"""
    try:
        pkpass_bytes = None
        with open("MyLoyaltyPass.pkpass", "rb") as f:
            print("Writing to file")
            pkpass_bytes = f.read()
        print(pkpass_bytes)
        return HttpResponse(pkpass_bytes, content_type="application/vnd.apple.pkpass", content_disposition="attachment; filename=MyLoyaltyPass.pkpass")
    except FileNotFoundError:
        return HttpResponse("Pass file not found. Please create a pass first.", status=404)

def test_page_view(request):
    """Serve a simple HTML page for testing pass download"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Apple Wallet Pass Test</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .button { 
                background-color: #007AFF; 
                color: white; 
                padding: 15px 30px; 
                text-decoration: none; 
                border-radius: 8px; 
                display: inline-block; 
                margin: 10px 0;
            }
            .info { background-color: #f0f0f0; padding: 15px; border-radius: 8px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>Apple Wallet Pass Test</h1>
        
        <div class="info">
            <h3>Important Notes:</h3>
            <ul>
                <li>You need valid Apple Developer certificates to create working passes</li>
                <li>The pass type identifier must match your Apple Developer account</li>
                <li>Team identifier must match your Apple Developer account</li>
                <li>Web service URL must be HTTPS and accessible</li>
            </ul>
        </div>
        
        <h2>Test Pass Download</h2>
        <a href="/pass/download" class="button">Download Test Pass</a>
        
        <h2>Create New Pass</h2>
        <form action="/pass/create" method="POST">
            <p><label>Customer ID: <input type="text" name="customer_id" value="test123"></label></p>
            <p><label>Background Color: <input type="text" name="backgroundColor" value="rgb(21, 21, 21)"></label></p>
            <p><label>Foreground Color: <input type="text" name="foregroundColor" value="rgb(255, 255, 255)"></label></p>
            <p><label>Label Color: <input type="text" name="labelColor" value="rgb(255, 255, 255)"></label></p>
            <input type="submit" value="Create Pass" class="button">
        </form>
    </body>
    </html>
    """
    return HttpResponse(html_content)
