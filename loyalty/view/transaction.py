from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from loyalty.models import Vendor, PassTemplate, Customer, Transaction, LoyaltyCard, Reward
from loyalty.serializers.serializers import TransactionSerializer
from loyalty.view.loyalty_pass import ping_apple_wallet
from rest_framework.permissions import IsAuthenticated
from django.db import transaction as db_transaction
from django.db.models import Q

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
    with db_transaction.atomic():
        transaction_obj = Transaction.objects.create(customer=customer, vendor=vendor, transaction_type=transaction_type,
                                                     transaction_amount=transaction_amount, points_remaining=loyalty_card.loyalty_points, transaction_points=transaction_points)
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
