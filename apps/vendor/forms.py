from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms

from django.contrib.auth.models import User

from apps.product.models import Product
from .models import Vendor, Customer

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'image', 'title',
                  'description', 'price', 'num_available', 'pickup_available']


# Vendor Sign Up Form
class VendorSignUpForm(UserCreationForm):
    company_name = forms.CharField(max_length=64, required=True)
    company_code = forms.CharField(max_length=64, required=True)
    address = forms.CharField(max_length=64, required=True)
    phone = forms.CharField(max_length=32, required=True)

    class Meta:
        model = User
        fields = [
        	'username',
        	'email',
        	'password1',
        	'password2',
        	'company_name',
        	'company_code',
            'address',
            'phone',
        ]

# Customer Sign Up Form
class CustomerSignUpForm(UserCreationForm):
    customername = forms.CharField(max_length=32)
    address = forms.CharField(max_length=64, required=True)
    phone = forms.CharField(max_length=32, required=True)

    class Meta:
        model = User
        fields = [
            'username',       	
        	'email',
        	'password1',
        	'password2',
            'customername',
            'address',
            'phone',
        ]