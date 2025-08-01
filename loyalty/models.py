from django.db import models

# Create your models here.
class LoyaltyCard(models.Model):
    customer_id = models.CharField(max_length=255)
    background_color = models.CharField(max_length=255)
    foreground_color = models.CharField(max_length=255)
    label_color = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    member_level = models.CharField(max_length=255)
    next_appointment = models.CharField(max_length=255)
    points = models.CharField(max_length=255)
    tier_progress = models.CharField(max_length=255)
    noOfAwards = models.CharField(max_length=255)
    membership_id = models.CharField(max_length=255)
    rewards_details = models.CharField(max_length=255)
    support = models.CharField(max_length=255)
    terms = models.CharField(max_length=255)
    locations = models.CharField(max_length=255)
    class Meta: 
        db_table = "loyalty_card"

    def __str__(self):
        return self.customer_id

    def __unicode__(self):
        return self.customer_id

    def __repr__(self):

class Vendor(models.Model): 
    vendorId = models.CharField(max_length=255)
    passTypeIdentifier = models.CharField(max_length=255)
    brandName = models.CharField(max_length=255)
    passTemplateId = models.IntegerField()
    logo = models.CharField(max_length=255)