from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from loyalty.models import Customer
from loyalty.serializers.serializers import CustomerSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

@api_view(["GET"])
def get_customers(request):
    permission_classes = [IsAuthenticated]
    search_query = request.query_params.get("search")
    print("search_query", search_query)
    print("request.user", request.user)
    customers = Customer.objects.filter(vendor=request.user, status="active")
    print("customers", customers)
    if search_query:
        customers = customers.filter(
            Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query) | Q(
                email__icontains=search_query) | Q(contact_number__icontains=search_query) | Q(id__icontains=search_query)
        )
    customers_data = CustomerSerializer(customers, many=True).data
    print("customers_data", customers_data)
    return Response({"message": "Customers fetched successfully", "customers": customers_data}, status=status.HTTP_200_OK)

@api_view(["PUT"])
def update_customer_status(request, customer_id):
    permission_classes = [IsAuthenticated]
    status_value = request.data.get("status")
    customer = Customer.objects.get(id=customer_id, vendor=request.user)
    customer.status = status_value
    customer.save()
    return Response({"customer": CustomerSerializer(customer).data})

@api_view(["GET"])
def fetch_customer(request, customer_id):
    customer = Customer.objects.get(id=customer_id, vendor=request.user)
    return Response({"customer": CustomerSerializer(customer).data})
