from rest_framework import serializers
from loyalty.models import FieldDefinition

class FieldDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldDefinition
        fields = "__all__"