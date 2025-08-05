import requests
import json

# Test data
test_data = {
    "customerDetails": {
        "name": "John Doe",
        "email": "john.doe@example.com"
    },
    "vendorDetails": {
        "name": "Tapbak Coffee Shop",
        "description": "Loyalty Card for Tapbak Coffee Shop",
        "colors": {
            "background": "rgb(0,122,255)",
            "foreground": "rgb(255,255,255)",
            "label": "rgb(255,255,255)"
        },
        "logo": "https://picsum.photos/160/160",
        "stripImage": "https://picsum.photos/320/123",
        "backgroundImage": "https://picsum.photos/320/123"
    }
}

# Make the request
url = "https://3942d4f5abba.ngrok-free.app/pass/create"

try:
    response = requests.post(
        url,
        json=test_data,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.apple.pkpass'
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'Not specified')}")
    print(f"Content-Length: {len(response.content)} bytes")
    
    if response.status_code == 200:
        # Save the pass file
        with open("test_pass.pkpass", "wb") as f:
            f.write(response.content)
        print("✅ Pass created successfully! Saved as 'test_pass.pkpass'")
        print("You can now open this file in Apple Wallet")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {e}") 