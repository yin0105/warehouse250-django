
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Vendor(models.Model):
    email = models.EmailField(max_length=150)
    company_name = models.CharField(max_length=255)
    company_code = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)
    products_limit = models.IntegerField(default=0)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.company_name

    def get_balance(self):
        items = self.items.filter(
            vendor_paid=False, order__vendors__in=[self.id])
        return sum((item.product.price * item.quantity) for item in items)

    def get_paid_amount(self):
        items = self.items.filter(
            vendor_paid=True, order__vendors__in=[self.id])
        return sum((item.product.price * item.quantity) for item in items)

    @receiver(post_save, sender=User)
    def create_user_vendor(sender, instance, created, **kwargs):
        if created:
            Vendor.objects.create(user=instance)

        try:
            instance.vendor.save()
            if instance.is_staff == True:
                Vendor.objects.last().delete()

        except Exception as e:
            pass


class Customer(models.Model):
    email = models.EmailField(max_length=150)
    customername = models.CharField(max_length=32)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.customername

    @receiver(post_save, sender=User)
    def create_user_customer(sender, instance, created, **kwargs):
        if created:
            Customer.objects.create(user=instance)

        try:
            instance.customer.save()
            if instance.is_staff == True:
                Customer.objects.last().delete()

        except Exception as e:
            pass


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=150)
    signup_confirmation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    @receiver(post_save, sender=User)
    def update_profile_signal(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
        instance.profile.save()
