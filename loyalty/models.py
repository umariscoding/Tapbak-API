from django.db import models
from uuid import uuid4

class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    business_name = models.CharField(max_length=255, null=False, blank=False)
    business_description = models.TextField(null=False, blank=False)
    email = models.EmailField(max_length=255, null=False, blank=False)
    password = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: 
        db_table = "vendor"

class Configuration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    background_color = models.CharField(max_length=255, null=False, blank=False)
    foreground_color = models.CharField(max_length=255, null=False, blank=False)
    label_color = models.CharField(max_length=255, null=False, blank=False)
    logo_url = models.URLField(null=False, blank=False)
    strip_image_url = models.URLField(null=False, blank=False)
    icon_url = models.URLField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: 
        db_table = "configuration"

class PassTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    configuration = models.ForeignKey(Configuration, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: 
        db_table = "pass_template"

class FieldDefinition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    data_type = models.CharField(max_length=50, null=False, blank=False)  # e.g., text, number, date
    suggested_section = models.CharField(
        choices=[
            ("header", "header"),
            ("primary", "primary"),
            ("secondary", "secondary"),
            ("back", "back"),
            ("auxiliary", "auxiliary"),
        ],
        max_length=20,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: 
        db_table = "field_definition"

class TemplateField(models.Model): 
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    pass_template = models.ForeignKey(PassTemplate, on_delete=models.PROTECT)
    field_definition = models.ForeignKey(FieldDefinition, on_delete=models.PROTECT)
    field_type = models.CharField(
        choices=[
            ("header", "header"),
            ("primary", "primary"),
            ("secondary", "secondary"),
            ("back", "back"),
            ("auxiliary", "auxiliary"),
        ],
        max_length=20,
        null=False,
        blank=False
    )
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: 
        db_table = "template_field"

class LoyaltyCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    loyalty_points = models.IntegerField(default=0, null=False, blank=False)
    authentication_token = models.UUIDField(null=False, blank=False)
    web_service_url = models.CharField(max_length=255, null=False, blank=False)
    serial_number = models.CharField(max_length=255, null=False, blank=False)
    meta_data = models.JSONField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: 
        db_table = "loyalty_card"

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    loyalty_card = models.ForeignKey(LoyaltyCard, on_delete=models.PROTECT, null=True, blank=True)
    class Meta: 
        db_table = "customer"
