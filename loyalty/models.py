from django.db import models
import uuid


class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    business_name = models.CharField(max_length=255, null=True, blank=True)
    business_description = models.TextField(null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vendor"


class Configuration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    background_color = models.CharField(max_length=255, null=True, blank=True)
    foreground_color = models.CharField(max_length=255, null=True, blank=True)
    label_color = models.CharField(max_length=255, null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    strip_image_url = models.URLField(null=True, blank=True)
    icon_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    points_system = models.CharField(max_length=255, null=True, blank=True, choices=[
                                     ("points", "points"), ("stamps", "stamps")])
    total_points = models.IntegerField(default=0, null=True, blank=True)
    class Meta:
        db_table = "configuration"


class PassTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    configuration = models.ForeignKey(
        Configuration, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pass_template"


class FieldDefinition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    data_type = models.CharField(max_length=50, null=True, blank=True)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    pass_template = models.ForeignKey(
        PassTemplate, on_delete=models.PROTECT, null=True, blank=True)
    field_definition = models.ForeignKey(
        FieldDefinition, on_delete=models.PROTECT, null=True, blank=True)
    field_type = models.CharField(
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
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "template_field"


class LoyaltyCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    loyalty_points = models.IntegerField(default=0, null=True, blank=True)
    authentication_token = models.UUIDField(null=True, blank=True)
    web_service_url = models.CharField(max_length=255, null=True, blank=True)
    serial_number = models.CharField(max_length=255, null=True, blank=True)
    meta_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "loyalty_card"


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    loyalty_card = models.ForeignKey(
        LoyaltyCard, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = "customer"
