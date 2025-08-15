from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from loyalty.models import Vendor, Configuration, PassTemplate, FieldDefinition, TemplateField, Customer, Transaction, LoyaltyCard, Reward
from django.db.models import Q
from loyalty.serializers.vendor import VendorSerializer, CustomerSerializer, TransactionSerializer
from loyalty.authentication import CookieJWTAuthentication
from loyalty.view.auth import CookieAuthentication
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
import boto3
import os
from django.conf import settings
from loyalty.view.loyalty_pass import ping_apple_wallet

@api_view(["POST"])
def create_vendor_view(request):
    name = request.data.get("name")
    email = request.data.get("email")
    business_name = request.data.get("business_name")
    business_description = request.data.get("business_description")
    password = request.data.get("password")
    print(name, email, business_name, business_description, password)
    existing_vendor = Vendor.objects.filter(email=email).first()
    if existing_vendor:
        return Response({"error": "Vendor already exists"}, status=status.HTTP_400_BAD_REQUEST)

    vendor = Vendor.objects.create(
        name=name,
        business_name=business_name,
        business_description=business_description,
        email=email,
        password=make_password(password)
    )
    vendor.save()

    configuration = Configuration.objects.create(
        background_color="#F2B4B8",
        foreground_color="#000000",
        label_color="#000000",
        points_system=None,
        total_points=0,
        logo_url="https://static.vecteezy.com/system/resources/previews/042/165/816/non_2x/google-logo-transparent-free-png.png",
        strip_image_url="https://logos-world.net/wp-content/uploads/2020/09/Google-Logo-1999-2010.jpg",
        icon_url="https://static.vecteezy.com/system/resources/previews/042/165/816/non_2x/google-logo-transparent-free-png.png",
    )

    pass_template = PassTemplate.objects.create(
        vendor=vendor,
        configuration=configuration,
    )

    field_definitions = FieldDefinition.objects.all()
    headerField = field_definitions.filter(suggested_section="header").first()

    TemplateField.objects.create(
        pass_template=pass_template,
        field_definition=headerField,
        field_type="header",
        position=0,
    )
    secondaryFields = field_definitions.filter(
        suggested_section="secondary"
    ).filter(
        Q(name__iexact="name") | Q(name__iexact="date of birth")
    )
    for field in secondaryFields:
        TemplateField.objects.create(
            pass_template=pass_template,
            field_definition=field,
            field_type="secondary",
            position=0 if field.name.lower() == "name" else 1,
        )

    return Response(VendorSerializer(vendor).data)


@csrf_exempt
@api_view(["POST"])
def login_view(request):
    email = request.data.get("email")
    password = request.data.get("password")
    vendor = Vendor.objects.filter(email=email).first()
    if not vendor:
        return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)
    if not vendor.check_password(password):
        return Response({"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)

    token = RefreshToken.for_user(vendor)
    vendor_data = {
        "id": vendor.id,
        "name": vendor.name,
        "email": vendor.email,
        "business_name": vendor.business_name,
        "business_description": vendor.business_description,
        "created_at": vendor.created_at,
        "access_token": str(token.access_token),
        "refresh_token": str(token)
    }
    response = Response({"message": "Login successful",
                        "vendor": vendor_data}, status=status.HTTP_200_OK)
    cookie_auth = CookieAuthentication()
    cookie_auth.set_access_token(response, token.access_token)
    cookie_auth.set_refresh_token(response, token)
    return response


@api_view(["GET"])
def get_statistics(request):
    permission_classes = [IsAuthenticated]
    print(request.user)
    vendor = Vendor.objects.get(id=request.user.id)
    total_customers = Customer.objects.filter(vendor=vendor).count()
    active_customers = Customer.objects.filter(
        vendor=vendor, status="active").count()
    total_transactions = Transaction.objects.filter(vendor=vendor).count()

    pass_template = PassTemplate.objects.filter(vendor=vendor).first()
    if pass_template and pass_template.configuration:
        configuration = pass_template.configuration
        points_system = configuration.points_system
        total_points = configuration.total_points
    else:
        points_system = "points"
        total_points = 0

    statistics = {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "total_transactions": total_transactions,
        "points_system": points_system,
        "total_points": total_points,
    }
    return Response({"message": "Statistics fetched successfully", "statistics": statistics}, status=status.HTTP_200_OK)


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
    # Get the configuration through the pass template
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
    pass_template = PassTemplate.objects.filter(vendor=request.user).first()
    configuration = pass_template.configuration
    fields = TemplateField.objects.filter(pass_template=pass_template)

    # Serialize the configuration and fields
    from loyalty.serializers.vendor import ConfigurationSerializer, TemplateFieldSerializer

    config_data = ConfigurationSerializer(configuration).data
    fields_data = TemplateFieldSerializer(fields, many=True).data

    return Response({
        "message": "Vendor config fetched successfully",
        "configuration": config_data,
        "fields": fields_data
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_field_definitions(request):
    field_definitions = FieldDefinition.objects.all()

    # Serialize the field definitions
    from loyalty.serializers.vendor import FieldDefinitionSerializer

    fields_data = FieldDefinitionSerializer(field_definitions, many=True).data

    return Response({
        "message": "Field definitions fetched successfully",
        "field_definitions": fields_data
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_customers(request):
    permission_classes = [IsAuthenticated]
    search_query = request.query_params.get("search")
    customers = Customer.objects.filter(vendor=request.user, status="active")
    if search_query:
        customers.filter(
            Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query) | Q(
                email__icontains=search_query) | Q(phone__icontains=search_query) | Q(id__icontains=search_query)
        )
    customers_data = CustomerSerializer(customers, many=True).data
    return Response({"message": "Customers fetched successfully", "customers": customers_data}, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_customer_status(request, customer_id):
    permission_classes = [IsAuthenticated]
    status = request.data.get("status")
    customer = Customer.objects.get(id=customer_id, vendor=request.user)
    customer.status = status
    customer.save()
    return Response({"customer": CustomerSerializer(customer).data})


@api_view(["PUT"])
def update_vendor(request):
    permission_classes = [IsAuthenticated]
    business_name = request.data.get("business_name")
    business_description = request.data.get("business_description")
    vendor = Vendor.objects.get(id=request.user.id)
    vendor.business_name = business_name
    vendor.business_description = business_description
    vendor.save()
    return Response({"vendor": VendorSerializer(vendor).data})


@api_view(["GET"])
def get_public_vendor(request, vendor_id):
    vendor = Vendor.objects.get(id=vendor_id)
    return Response({"business_name": vendor.business_name, "business_description": vendor.business_description})


@api_view(["POST"])
def upload_image(request):
    settings.STORAGES['default'] = settings.STORAGES['s3']
    file = request.FILES.get("file")
    file_name = file.name
    print(file_name)
    file_url = upload_image_to_s3(file)
    settings.STORAGES['default'] = settings.STORAGES['default']
    return Response({"message": "File uploaded successfully", "url": file_url}, status=status.HTTP_200_OK)


def upload_image_to_s3(file):

    s3 = boto3.client('s3')
    s3.upload_fileobj(file, os.getenv(
        "AWS_STORAGE_BUCKET_NAME"), "listings/" + file.name)
    return f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.amazonaws.com/listings/{file.name}"


@api_view(["GET"])
def fetch_customer(request, customer_id):
    customer = Customer.objects.get(id=customer_id, vendor=request.user)
    return Response({"customer": CustomerSerializer(customer).data})


@api_view(["POST"])
def process_transaction(request):
    permission_classes = [IsAuthenticated]
    vendor = Vendor.objects.get(id=request.user.id)
    passTemplate = PassTemplate.objects.get(vendor=vendor)
    customer_id = request.data.get("customer_id")
    transaction_type = request.data.get("transaction_type")
    transaction_amount = request.data.get("transaction_amount")
    transaction_points = request.data.get("transaction_points")
    customer = Customer.objects.get(id=customer_id, vendor=vendor)

    loyalty_card = LoyaltyCard.objects.get(id=customer.loyalty_card.id)
    loyalty_card.loyalty_points += int(transaction_points)
    print(loyalty_card.loyalty_points,
          passTemplate.configuration.total_points, transaction_points)
    with transaction.atomic():
        transaction_obj = Transaction.objects.create(customer=customer, vendor=vendor, transaction_type=transaction_type,
                                                     transaction_amount=transaction_amount, points_remaining=loyalty_card.loyalty_points, transaction_points=transaction_points)

        # Keep creating rewards as long as there are enough points
        while loyalty_card.loyalty_points >= passTemplate.configuration.total_points:
            loyalty_card.reward_available = True
            loyalty_card.loyalty_points -= passTemplate.configuration.total_points
            Reward.objects.create(customer=customer, status="available")
        loyalty_card.save()
    ping_apple_wallet(customer.loyalty_card.serial_number)
    return Response({"message": "Transaction processed successfully"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_transactions(request):
    permission_classes = [IsAuthenticated]
    vendor = Vendor.objects.get(id=request.user.id)
    if (request.query_params.get("search_query")):
        search_query = request.query_params.get("search_query")
        results = Transaction.objects.filter(
            vendor=vendor
        ).filter(
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(customer__email__icontains=search_query) |
            Q(customer__contact_number__icontains=search_query) |
            Q(customer__id__icontains=search_query) |
            Q(id__icontains=search_query)
        ).order_by("-created_at")    
        return Response({"transactions": TransactionSerializer(results, many=True).data}, status=status.HTTP_200_OK)
    else:
        results = Transaction.objects.filter(
            vendor=vendor).order_by("-created_at")
        return Response({"transactions": TransactionSerializer(results, many=True).data}, status=status.HTTP_200_OK)
