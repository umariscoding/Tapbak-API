from django_walletpass.models import PassBuilder


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
