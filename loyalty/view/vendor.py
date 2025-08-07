from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from loyalty.models import Vendor, Configuration, PassTemplate, FieldDefinition, TemplateField
from django.db.models import Q

@api_view(["POST"])
def create_vendor_view(request):
    vendor = Vendor.objects.create(
        business_name = "Ahmed Gul",
        business_description = "Ahmed Gul's Business",
        email = "ahmedgul@gmail.com",
        password = "123456",
    )
    configuration = Configuration.objects.create(
        background_color = "#F2B4B8",
        foreground_color = "#000000",
        label_color = "#000000",
        logo_url = "https://static.vecteezy.com/system/resources/previews/042/165/816/non_2x/google-logo-transparent-free-png.png",
        strip_image_url = "https://logos-world.net/wp-content/uploads/2020/09/Google-Logo-1999-2010.jpg",
        icon_url = "https://static.vecteezy.com/system/resources/previews/042/165/816/non_2x/google-logo-transparent-free-png.png",
    )

    pass_template = PassTemplate.objects.create(
        vendor = vendor,
        configuration = configuration,
    )

    field_definitions = FieldDefinition.objects.all()
    headerField = field_definitions[0]
    print(field_definitions, headerField)
    TemplateField.objects.create(
        pass_template = pass_template,
        field_definition = headerField,
        field_type = "header",
        position = 0,
    )
    secondaryFields = field_definitions.filter(
        suggested_section="secondary"
    ).filter(
       Q(name__iexact = "name") | Q(name__iexact = "date of birth")
    )
    print(secondaryFields)
    for field in secondaryFields:
        print("Field", field, pass_template, "created")
        TemplateField.objects.create(
            pass_template = pass_template,
            field_definition = field,
            field_type = "secondary",
            position = 0 if field.name.lower() == "name" else 1,
        )

    
    print("Header Field", headerField.name, "created")


    return Response(status=status.HTTP_201_CREATED)
