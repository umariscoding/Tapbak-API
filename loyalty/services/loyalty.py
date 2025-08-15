import uuid
import os
from datetime import datetime
from django_walletpass.models import PassBuilder
import requests
from PIL import Image
import io
from dotenv import load_dotenv
load_dotenv()

class LoyaltyService:
    def __init__(self, request, context):
        self.request = request
        self.context = context
        self.builder = PassBuilder()

    def create_pass_json(self, serialNumber = uuid.uuid4(), authenticationToken = uuid.uuid4()):
        self.builder.pass_data_required.update({
            "passTypeIdentifier": os.getenv("PASS_TYPE_ID"),
            "teamIdentifier": os.getenv("TEAM_ID"),
            "organizationName": os.getenv("ORGANIZATION_NAME"),
            "serialNumber": str(serialNumber),
            "webServiceURL": os.getenv("WEB_SERVICE_URL"),
            "authenticationToken": str(authenticationToken),
            "description": self.context["vendor"].business_name,
        })

        secondaryFields = []
        headerFields = []
        for field in self.context["secondaryFields"]:
            secondaryFields.append({
                "key": field.field_definition.name,
                "label": field.field_definition.name,
                "value": self.get_value(field),
                "changeMessage": "0"
            })
        headerFields.append({
            "key": self.context["headerField"].field_definition.name,
            "label": self.context["headerField"].field_definition.name,
            "value": self.get_value(self.context["headerField"]),
            "changeMessage": "0"
        })
        self.builder.pass_data.update({
            "formatVersion": 1,
            "backgroundColor": self.context['passTemplate'].configuration.background_color,
            "foregroundColor": self.context['passTemplate'].configuration.foreground_color,
            "labelColor": self.context['passTemplate'].configuration.label_color,
            "logoText": self.context["vendor"].business_name,
            "images": {
                "icon": "icon.png",
                "logo": "logo.png",
                "stripImage": "strip.png"
            },

            "barcode": {
                "message": str(self.context["customer"].id),
                "format": "PKBarcodeFormatQR",
                "messageEncoding": "iso-8859-1"
            },
            "storeCard": {
                "headerFields": headerFields,
                "secondaryFields": secondaryFields
            }
        })
        self.getImages()
        loyalty_metadata = {
            "headerFields": headerFields,
            "secondaryFields": secondaryFields
        }
        pkbytes = self.builder.build()
        return pkbytes, {
            "authenticationToken": str(authenticationToken),
            "serialNumber": str(serialNumber),
            "loyalty_metadata": loyalty_metadata
        }

    def get_value(self, formDefinition):
        match (formDefinition.field_definition.name.lower()):
            case "name":
                return self.context["customer"].first_name + " " + self.context["customer"].last_name
            case "date of birth":
                dob = self.context["customer"].date_of_birth
                return dob.isoformat() if dob else ""
            case "email":
                return self.context["customer"].email
            case "phone":
                return self.context["customer"].phone
            case "loyalty points":
                return self.context["customer"].loyalty_card.loyalty_points if self.context["customer"].loyalty_card else 0
            case "rewards":
                return self.context["noOfRewards"]
            case "award_available":
                return self.context["customer"].loyalty_card.reward_available if self.context["customer"].loyalty_card else 0
            case _:
                return ""

    def getImages(self):
        if self.context["passTemplate"].configuration.icon_url:
            icon_url = self.context["passTemplate"].configuration.icon_url
            icon_data = requests.get(icon_url).content
            self.builder.add_file("icon.png", icon_data)
        
        if self.context["passTemplate"].configuration.logo_url:
            logo_url = self.context["passTemplate"].configuration.logo_url
            logo_data = requests.get(logo_url).content
            self.builder.add_file("logo.png", logo_data)

        if self.context["passTemplate"].configuration.points_system == "stamps":
                self.generate_image()
        elif self.context["passTemplate"].configuration.strip_image_url:
                strip_image_url = self.context["passTemplate"].configuration.strip_image_url
                strip_image_data = requests.get(strip_image_url).content
                self.builder.add_file("strip.png", strip_image_data)

    def generate_image(self):
        loyalty_points = 0
        total_points = self.context["passTemplate"].configuration.total_points
        number_of_rows = 1 if total_points <= 5 else 2
        all_image = Image.new("RGBA", (1125, 432))
        points_image = Image.open(os.path.join(os.path.dirname(__file__), 'public', 'filled.png'))
        points_image = points_image.resize((200, 200)).convert("RGBA")

        remaining_points_image = Image.open(os.path.join(os.path.dirname(__file__), 'public', 'not_filled.png'))
        remaining_points_image = remaining_points_image.resize((200, 200)).convert("RGBA")
       
        stamp_width = 200
        stamp_height = 200
        total_stamps_per_row = 5
        
        total_stamps_width = total_stamps_per_row * stamp_width
        
        bg_width = all_image.width
        x_offset = (bg_width - total_stamps_width) // 2
        
        bg_height = all_image.height
        total_stamps_height = number_of_rows * stamp_height
        y_offset = (bg_height - total_stamps_height) // 2
        
        for i in range(number_of_rows):
            for j in range(5):
                x_pos = x_offset + (j * stamp_width)
                y_pos = y_offset + (i * stamp_height)
                
                if j < loyalty_points:
                    all_image.paste(points_image, (x_pos, y_pos), points_image)
                else:
                    all_image.paste(remaining_points_image, (x_pos, y_pos), remaining_points_image)
            
            if number_of_rows > 1 and i == 0:
                loyalty_points_second_row = loyalty_points - 5
                for k in range(5):
                    x_pos = x_offset + (k * stamp_width)
                    y_pos = y_offset + ((i + 1) * stamp_height)
                    
                    if k < loyalty_points_second_row:
                        all_image.paste(points_image, (x_pos, y_pos), points_image)
                    else:
                        all_image.paste(remaining_points_image, (x_pos, y_pos), remaining_points_image)

        img_byte_arr = io.BytesIO()
        all_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        image_bytes = img_byte_arr.getvalue()
        
        self.builder.add_file("strip.png", image_bytes)