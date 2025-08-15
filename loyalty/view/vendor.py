from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from loyalty.models import Vendor, Configuration, PassTemplate, FieldDefinition, TemplateField
from django.db.models import Q
from loyalty.serializers.serializers import VendorSerializer
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


@api_view(["POST"])
def create_vendor_view(request):
    name = request.data.get("name")
    email = request.data.get("email")
    business_name = request.data.get("business_name")
    business_description = request.data.get("business_description")
    password = request.data.get("password")
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
    if headerField:
        TemplateField.objects.create(
            pass_template=pass_template,
            field_definition=headerField,
            field_type="header",
            position=0,
        )
    print("headerField", headerField)
    secondaryFields = field_definitions.filter(
        suggested_section="secondary"
    ).filter(
        Q(name__iexact="name") | Q(name__iexact="date of birth")
    )
    print("secondaryFields", secondaryFields)
    for field in secondaryFields:
        TemplateField.objects.create(
            pass_template=pass_template,
            field_definition=field,
            field_type="secondary",
            position=0 if field.name.lower() == "name" else 1,
        )
    token = RefreshToken.for_user(vendor)
    vendor_data = VendorSerializer(vendor).data
    return Response({"message": "Signup successful", "vendor": vendor_data, "token": str(token.access_token)}, status=status.HTTP_201_CREATED)


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
    return response


@api_view(["GET"])
def get_statistics(request):
    permission_classes = [IsAuthenticated]
    from loyalty.models import Customer, Transaction, PassTemplate
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
