from rest_framework import serializers
from loyalty.models import Vendor, Configuration, TemplateField, FieldDefinition, Customer, LoyaltyCard, Transaction


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"


class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = "__all__"


class FieldDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldDefinition
        fields = "__all__"


class LoyaltyCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyCard
        fields = "__all__"


class TemplateFieldSerializer(serializers.ModelSerializer):
    field_definition = FieldDefinitionSerializer(read_only=True)

    class Meta:
        model = TemplateField
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    loyalty_card = LoyaltyCardSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"
