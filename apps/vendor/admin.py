from django.contrib import admin



from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from . models import Vendor, Customer, Profile

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class VendorInline(admin.StackedInline):
    model = Vendor
    can_delete = False
    verbose_name_plural = 'vendor'

class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    verbose_name_plural = 'customer'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (VendorInline, CustomerInline)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)




admin.site.register(Vendor)
admin.site.register(Customer)
admin.site.register(Profile)