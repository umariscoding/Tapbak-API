from django_walletpass.models import PassBuilder
import requests


def create_pass(customer_id, background_color, foreground_color, label_color, name, member_level, next_appointment, points, tier_progress, expires, balance, membership_id, rewards_details, support, terms, locations, relevant_date):
    builder = PassBuilder()
    builder.pass_data_required.update(
        {
            "serialNumber": f"patient-{customer_id}",
            "description": "Upcoming Appointment",
            "organizationName": "Tap",
        }
    )

    builder.pass_data.update(
        {
            "formatVersion": 1,
            "passTypeIdentifier": "pass.co.tapback.loyalty",
            "teamIdentifier": "QK2FSS3243",
            "serialNumber": f"patient-{customer_id}",
            "organizationName": "Tap",
            "description": "Upcoming Appointment",
            "backgroundColor": background_color,
            "foregroundColor": foreground_color,
            "labelColor": label_color,
            "barcode": {
                "message": "987654321",
                "format": "PKBarcodeFormatPDF417",
                "messageEncoding": "iso-8859-1",
            },
            "storeCard": {
                "headerFields": [
                    {
                        "key": "member_level",
                        "label": "MEMBER LEVEL",
                        "value": member_level,
                        "textAlignment": "PKTextAlignmentCenter",
                    }
                ],
                "primaryFields": [
                    {
                        "key": "name",
                        "label": "Member",
                        "value": name,
                        "textAlignment": "PKTextAlignmentLeft",
                    },
                    {
                        "key": "next_appointment",
                        "label": "Next Appointment",
                        "value": next_appointment,
                        "dateStyle": "PKDateStyleMedium",
                        "timeStyle": "PKDateStyleShort",
                        "textAlignment": "PKTextAlignmentRight",
                    },
                ],
                "secondaryFields": [
                    {
                        "key": "points",
                        "label": "Reward Points",
                        "value": points,
                        "textAlignment": "PKTextAlignmentRight",
                    },
                    {
                        "key": "tier_progress",
                        "label": "Progress to Diamond",
                        "value": tier_progress,
                        "textAlignment": "PKTextAlignmentLeft",
                    },
                ],
                "auxiliaryFields": [
                    {
                        "key": "expires",
                        "label": "Card Expires",
                        "value": expires,
                        "dateStyle": "PKDateStyleShort",
                        "textAlignment": "PKTextAlignmentLeft",
                    },
                    {
                        "key": "balance",
                        "label": "Credit Balance",
                        "value": balance,
                        "textAlignment": "PKTextAlignmentCenter",
                    },
                ],
            },
            "backFields": [
                {
                    "key": "membership_id",
                    "label": "Membership ID",
                    "value": membership_id,
                    "textAlignment": "PKTextAlignmentLeft",
                },
                {
                    "key": "rewards_details",
                    "label": "Rewards Notes",
                    "value": rewards_details,
                    "textAlignment": "PKTextAlignmentNatural",
                },
                {
                    "key": "support",
                    "label": "Support",
                    "value": "help@tapbak.com \u2022 +44 20 7946 0958",
                    "textAlignment": "PKTextAlignmentLeft",
                },
                {
                    "key": "terms",
                    "label": "Terms & Conditions",
                    "value": "Valid at participating locations only. Points expire after 12 months of inactivity.",
                    "textAlignment": "PKTextAlignmentLeft",
                },
            ],
            "locations": [
                {
                    "latitude": 51.5074,
                    "longitude": -0.1278,
                    "relevantText": "TapBak London Clinic",
                }
            ],
            "relevantDate": "2025-08-15T14:30:00Z",
            "userInfo": {"preferredLanguage": "en"},
        }
    )

    pkpass_bytes = builder.build()
    pkpass_file = open("mypass.pkpass", "wb")
    pkpass_file.write(pkpass_bytes)
    return pkpass_bytes


def send_push_notification(pass_obj, message=None):
    """
    Send push notification to all devices registered for a specific pass
    
    Args:
        pass_obj: Pass instance
        message: Optional message to display (default: "Your pass has been updated")
    """
    if not message:
        message = "Your pass has been updated"
    
    # Get all registrations for this pass
    registrations = pass_obj.registrations.all()
    
    if not registrations.exists():
        print(f"No devices registered for pass {pass_obj.serial_number}")
        return 0, 0
    
    # Apple Push Notification Service endpoint
    apns_url = "https://api.push.apple.com/3/device/"
    
    # Headers for APNS
    headers = {
        'apns-topic': pass_obj.pass_type_identifier,
        'apns-push-type': 'alert',
        'Content-Type': 'application/json'
    }
    
    # Payload for the notification
    payload = {
        'aps': {
            'alert': message,
            'badge': 1,
            'sound': 'default'
        }
    }
    
    success_count = 0
    failed_count = 0
    
    for registration in registrations:
        try:
            # Send push notification to each device
            response = requests.post(
                f"{apns_url}{registration.push_token}",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                success_count += 1
                print(f"Push notification sent successfully to device {registration.device_library_identifier}")
            else:
                failed_count += 1
                print(f"Failed to send push notification to device {registration.device_library_identifier}. Status: {response.status_code}")
                
                # If token is invalid, remove the registration
                if response.status_code in [400, 410]:
                    print(f"Removing invalid registration for device {registration.device_library_identifier}")
                    registration.delete()
                    
        except Exception as e:
            failed_count += 1
            print(f"Error sending push notification to device {registration.device_library_identifier}: {str(e)}")
    
    print(f"Push notifications sent: {success_count} successful, {failed_count} failed")
    return success_count, failed_count


def send_push_to_all_passes(pass_type_id, message=None):
    """
    Send push notification to all passes of a specific type
    
    Args:
        pass_obj: Pass type identifier
        message: Optional message to display
    """
    from django_walletpass.models import Pass
    
    passes = Pass.objects.filter(pass_type_identifier=pass_type_id)
    
    total_success = 0
    total_failed = 0
    
    for pass_obj in passes:
        success, failed = send_push_notification(pass_obj, message)
        total_success += success
        total_failed += failed
    
    print(f"Total push notifications sent: {total_success} successful, {total_failed} failed")
    return total_success, total_failed


def update_pass_and_notify(pass_obj, updated_data, message=None):
    """
    Update a pass and send push notification to all registered devices
    
    Args:
        pass_obj: Pass instance to update
        updated_data: Dictionary containing updated pass data
        message: Optional message for push notification
    """
    try:
        # Update the pass data
        for key, value in updated_data.items():
            if hasattr(pass_obj, key):
                setattr(pass_obj, key, value)
        
        pass_obj.save()
        
        # Send push notification
        success, failed = send_push_notification(pass_obj, message)
        
        print(f"Pass {pass_obj.serial_number} updated and notification sent")
        return True, success, failed
        
    except Exception as e:
        print(f"Error updating pass {pass_obj.serial_number}: {str(e)}")
        return False, 0, 0
