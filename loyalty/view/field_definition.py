from rest_framework.decorators import api_view
from rest_framework.response import Response
from loyalty.models import FieldDefinition
from loyalty.serializers.field_definition import FieldDefinitionSerializer

@api_view(["GET"])
def get_field_definitions(request):
    field_definitions = FieldDefinition.objects.all()
    serializer = FieldDefinitionSerializer(field_definitions, many=True)
    return Response(serializer.data)