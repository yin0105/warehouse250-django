from django.contrib import admin



from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from . models import Vendor, Customer, Profile

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton


def company_name(obj):
    return '%s' % (obj.company_name)

company_name.short_description = 'Name'

def company_code(obj):
    return '%s' % (obj.company_code)

company_code.short_description = 'Code'


def vendor_disable(modeladmin, request, queryset):
    for vendor in queryset:
        vendor.enabled = False
        vendor.save()
    return

vendor_disable.short_description = 'Disable'


def vendor_enabled(modeladmin, request, queryset):
    for vendor in queryset:
        vendor.enabled = True
        vendor.save()
    return

vendor_enabled.short_description = 'Enabled'

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

class CustomerAdmin(admin.ModelAdmin):    
    list_display = ['customername', 'email', 'address', 'phone', 'created_at']
    ordering = ['customername']
    search_fields = ['customername', 'email', 'address', 'phone']


class VendorAdmin(admin.ModelAdmin):
    list_display = [company_name, company_code, 'email', 'address', 'phone', 'created_at', 'enabled']
    ordering = ['company_name']
    search_fields = [company_name, company_code, 'email', 'address', 'phone']

    actions = [vendor_disable, vendor_enabled]

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)




admin.site.register(Vendor, VendorAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Profile)