from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms

from django.contrib.auth.models import User

from apps.product.models import Product,ProductImage
from .models import Vendor, Customer


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'title',
        # fields = ['category', 'image', 'title',
                  'description', 'price', 'discount', 'num_available', 'pickup_available']

class ProductImageForm(ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']


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
class RestorePasswordForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)


class RequestRestorePasswordForm(forms.Form):
    email = forms.EmailField()


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