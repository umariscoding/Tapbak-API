from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from loyalty.services.loyalty import upload_image_to_s3

@api_view(["POST"])
def upload_image(request):
    settings.STORAGES['default'] = settings.STORAGES['s3']
    file = request.FILES.get("file")
    file_name = file.name
    file_url = upload_image_to_s3(file)
    settings.STORAGES['default'] = settings.STORAGES['default']
    return Response({"message": "File uploaded successfully", "url": file_url}, status=status.HTTP_200_OK)
