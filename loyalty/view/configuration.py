from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from loyalty.models import PassTemplate, FieldDefinition, TemplateField
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from loyalty.serializers.serializers import ConfigurationSerializer, TemplateFieldSerializer, FieldDefinitionSerializer

# Configuration and template management views

def save_configuration(request):
    data = request.data.get("configuration")
    config_data = {
        "background_color": data["background_color"],
        "foreground_color": data["foreground_color"],
        "label_color": data["label_color"],
        "points_system": data["points_system"],
        "total_points": data["total_points"],
        "logo_url": data["logo_url"],
        "strip_image_url": data["strip_image_url"],
        "icon_url": data["icon_url"]
    }
    pass_template = PassTemplate.objects.filter(vendor=request.user).first()
    if pass_template and pass_template.configuration:
        configuration = pass_template.configuration
        for key, value in config_data.items():
            setattr(configuration, key, value)
        configuration.save()
        return Response({"message": "Configuration saved successfully"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Configuration not found"}, status=status.HTTP_404_NOT_FOUND)

def save_fields(request):
    fields = request.data.get("fields")
    if not fields or fields[0] == None: 
        return Response({"message": "No fields to save"}, status=status.HTTP_200_OK)
    pass_template = PassTemplate.objects.filter(vendor=request.user).first()
    for field in fields:
        field_definition = FieldDefinition.objects.get(id=field)
        TemplateField.objects.update_or_create(
            pass_template=pass_template,
            field_definition=field_definition,
            field_type=field_definition.suggested_section,
            position=0
        )
    return Response({"message": "Fields saved successfully"}, status=status.HTTP_200_OK)

@api_view(["POST"])
def save_vendor_config(request):
    permission_classes = [IsAuthenticated]
    with transaction.atomic():
        save_configuration(request)
        save_fields(request)
    return Response({"message": "Vendor config saved successfully"}, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_vendor_config(request):
    permission_classes = [IsAuthenticated]
    print("request.user", request.user)
    pass_template = PassTemplate.objects.filter(vendor=request.user).first()
    print("pass_template", pass_template)
    configuration = pass_template.configuration
    fields = TemplateField.objects.filter(pass_template=pass_template)
    print("fields", fields)
    config_data = ConfigurationSerializer(configuration).data
    fields_data = TemplateFieldSerializer(fields, many=True).data
    print("fields_data", len(fields_data))
    return Response({
        "message": "Vendor config fetched successfully",
        "configuration": config_data,
        "fields": fields_data
    }, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_field_definitions(request):
    field_definitions = FieldDefinition.objects.all()
    serializer = FieldDefinitionSerializer(field_definitions, many=True)
    return Response(serializer.data)