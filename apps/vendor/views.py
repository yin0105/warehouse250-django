from apps.coupon.models import Coupon
from django.shortcuts import render, redirect,  get_object_or_404, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm,  AuthenticationForm
from django.utils.text import slugify

from django.contrib.auth.models import User
from .models import Vendor, Customer
from apps.product.models import Product, ProductImage
from apps.order.models import Order, OrderItem

from .forms import ProductForm, ProductImageForm, VendorSignUpForm, CustomerSignUpForm, RestorePasswordForm, RequestRestorePasswordForm

from django.utils.encoding import force_text

from django.db import IntegrityError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token
from django.template.loader import render_to_string

from django.core.exceptions import ObjectDoesNotExist

from django.core.mail import send_mail

from django.contrib.auth.views import (
    LogoutView as BaseLogoutView, PasswordChangeView as BasePasswordChangeView,
    PasswordResetDoneView as BasePasswordResetDoneView, PasswordResetConfirmView as BasePasswordResetConfirmView,
)


def login_request(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        username = request.POST['username']
        password = request.POST['password']

        username = User.objects.get(email=username)

        user = authenticate(
            request, username=username.username, password=password)

        if user:
            login(request, user)
            if user.is_superuser:
                print("=== superuser")
                try:
                    request.session['username'] = username.username
                except:
                    pass
                return redirect("/dashboard/")
            try:
                customer = Customer.objects.get(email=username)
                request.session['username'] = customer.customername
                request.session['phone'] = customer.phone
                request.session['address'] = customer.address
                request.session['customer'] = True
                try:
                    orders = []
                    for row in Order.objects.filter(email=username):
                        order = {}
                        order["created_at"] = row.created_at.strftime("%Y/%m/%d, %H:%M:%S")
                        order["status"] = row.status
                        items = []
                        total_quantity = 0
                        subtotal_amount = 0
                        for item_ in OrderItem.objects.filter(order_id=row.id).select_related("product"):
                            item = {}
                            item["product_title"] = item_.product.title
                            item["quantity"] = str(item_.quantity)
                            item["price"] = str(item_.price)
                            total_quantity += item_.quantity
                            subtotal_amount += item_.price
                            items.append(item)
                        order["items"] = items
                        order["subtotal_amount"] = str(subtotal_amount)
                        order["total_quantity"] = str(total_quantity)
                        order["paid_amount"] = str(row.paid_amount)
                        order["delivery_cost"] = str(row.delivery_cost)
                        coupon_discount = ""
                        coupon_code = str(row.used_coupon)
                        if coupon_code != "None":
                            try:
                                coupon = Coupon.objects.get(code=coupon_code)
                                if coupon:
                                    coupon_discount = str(coupon.discount) + " %"
                            except:
                                pass
                        order["coupon_discount"] = coupon_discount
                        orders.append(order)
                    
                    request.session['orders'] = orders
                    return redirect('myaccount')
                except Exception as e:
                    print(e)
                
                
            except Exception as e:
                pass

            try:
                vendor = Vendor.objects.get(email=username).company_name
                request.session['username'] = vendor
            except Exception as e:
                pass

            messages.info(request, f"You are now logged in as { username }.")
            return redirect("vendor_admin")

        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "vendor/login.html", {'form': form})


def logout_request(request):
    try:
        if request.session['username']:
            del request.session['username']
    except Exception as e:
        pass

    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('frontpage')


def email_user(who, subject, message, from_email=None, **kwargs):
    """Send an email to this user."""
    send_mail(subject, message, from_email, [who.email], **kwargs)


def activation_sent_view(request):
    return render(request, 'activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true
        user.is_active = True
        # set signup_confirmation true
        user.profile.signup_confirmation = True
        user.save()
        # login(request, user)
        messages.success(request, ('Your account have been confirmed.'))
        return redirect('login')
    else:
        # return render(request, 'activation_invalid.html')
        messages.warning(
            request, ('The confirmation link was invalid, possibly because it has already been used.'))
        return redirect('frontpage')


def activate_password(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print("uid = ", uid)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    print("user = ", user)
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        print("=== set password")
        # user = User.objects.filter(pk=uid).first()
        user.password = ""
        user.save()
        messages.success(request, ('Your password reset request has been approved.'))
        return redirect('restore_password')
    else:
        # return render(request, 'activation_invalid.html')
        messages.warning(
            request, ('The confirmation link was invalid, possibly because it has already been used.'))
        return redirect('frontpage')


def become_vendor(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        form = VendorSignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            user.refresh_from_db()

            user.username = form.cleaned_data.get('email')

            user.is_active = False
            user.profile.email = form.cleaned_data.get('email')

            user.vendor.email = form.cleaned_data.get('email')
            user.vendor.company_name = form.cleaned_data.get('company_name')
            user.vendor.company_code = form.cleaned_data.get('company_code')
            user.vendor.address = form.cleaned_data.get('address')
            user.vendor.phone = form.cleaned_data.get('phone')

            user.save()

            Customer.objects.last().delete()

            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            # load a template like get_template()
            # and calls its render() method immediately.
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            message = render_to_string('activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                # method will generate a hash value with user related data
                'token': token,
            })
            print("uid =", uid, "; token=", token)
            email_user(user, subject, message)

            messages.success(
                request, ('Please check your email for verification'))

            return redirect('activation_sent')
    else:
        form = VendorSignUpForm()

    return render(request, 'vendor/become_vendor.html', {'form': form})


@login_required
def vendor_admin(request):
    try:
        vendor = request.user.vendor
    except ObjectDoesNotExist:
        return redirect('frontpage')
    else:
        products = vendor.products.all()
        orders = vendor.orders.all()

        for order in orders:
            order.vendor_amount = 0
            order.vendor_paid_amount = 0
            order.fully_paid = True
            coupon_discount = 0
            coupon_code = str(order.used_coupon)
            if coupon_code != "None":
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    
                    if coupon:
                        coupon_discount = coupon.discount
                except:
                    pass
            order.coupon_discount = coupon_discount

            for item in order.items.all():
                if item.vendor == request.user.vendor:
                    if item.vendor_paid:
                        order.vendor_paid_amount += item.get_total_price()
                    else:
                        order.vendor_amount += item.get_total_price()
                        order.fully_paid = False

        return render(request, 'vendor/vendor_admin.html', {'vendor': vendor, 'products': products, 'orders': orders})


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.slug = slugify(product.title)
            product.save()

            return redirect('vendor_admin')
    else:
        vendor = request.user.vendor
        products = len(Product.objects.filter(vendor=vendor))
        print(" vendor:: products  ", products, vendor.products_limit)
        form = ProductForm()

    return render(request, 'vendor/add_product.html', {'form': form})


@login_required
def edit_product(request, pk):
    vendor = request.user.vendor
    product = vendor.products.get(pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()

            return redirect('vendor_admin')
    else:
        form = ProductForm(instance=product)

    return render(request, 'vendor/edit_product.html', {'form': form, 'product': product})


@login_required
def edit_productimage(request, pk):
    vendor = request.user.vendor
    # product = vendor.products.get(pk=pk)
    product_images = ProductImage.objects.filter(product=pk)
    
    if request.method == 'POST':
        
        form = ProductImageForm(request.POST, request.FILES)
        if "image" in request.FILES and len(request.FILES["image"]) > 0:
            product = Product.objects.get(id=pk)
            product_image = ProductImage.objects.create(product=product, image=request.FILES["image"])
        # product_image.save()
        # if form.is_valid():
        #     form.save()

        return redirect('vendor_admin')
    else:
        form = ProductImageForm()

    return render(request, 'vendor/edit_productimage.html', {'product_images': product_images, 'form': form})


@login_required
def del_productimage(request, pk):
    vendor = request.user.vendor
    # product = vendor.products.get(pk=pk)
    product_image = ProductImage.objects.filter(id=pk).first()
    product_id = product_image.product.id
    product_image.delete()
    product_images = ProductImage.objects.filter(product=product_id)


    # if request.method == 'POST':
    #     form = ProductForm(request.POST, request.FILES, instance=product)

    #     if form.is_valid():
    #         form.save()

    #         return redirect('vendor_admin')
    # else:
    #     form = ProductForm(instance=product)

    # return render(request, 'vendor/edit_productimage.html', {'product_images': product_images})
    return redirect("edit_productimage", pk=product_id)



@login_required
def edit_vendor(request):
    vendor = request.user.vendor

    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')

        if name:
            vendor.created_by.email = email
            vendor.created_by.save()

            vendor.name = name
            vendor.save()

            return redirect('vendor_admin')

    return render(request, 'vendor/edit_vendor.html', {'vendor': vendor})


def vendors(request):
    vendors = Vendor.objects.filter(enabled=True)

    return render(request, 'vendor/vendors.html', {'vendors': vendors})


def vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, pk=vendor_id)

    return render(request, 'vendor/vendor.html', {'vendor': vendor})


def become_customer(request):
    if request.user.is_authenticated:
        logout(request)
    
    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            user.refresh_from_db()

            user.username = form.cleaned_data.get('email')

            user.is_active = False
            user.profile.email = form.cleaned_data.get('email')

            user.customer.customername = form.cleaned_data.get('customername')
            user.customer.email = form.cleaned_data.get('email')
            user.customer.address = form.cleaned_data.get('address')
            user.customer.phone = form.cleaned_data.get('phone')

            user.save()
            Vendor.objects.last().delete()

            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            # load a template like get_template()
            # and calls its render() method immediately.
            message = render_to_string('activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })
            email_user(user, subject, message)

            messages.success(
                request, ('Please check your email for verification'))

            return redirect('activation_sent')
    else:
        form = CustomerSignUpForm()

    return render(request, 'customer/become_customer.html', {'form': form})


@login_required
def myaccount(request):
    return render(request, 'customer/myaccount.html')


def request_restore_password(request):
    if request.method == 'POST':
        form = RequestRestorePasswordForm(request.POST)

        if form.is_valid():
            user = User.objects.filter(email=form.cleaned_data.get('email')).first()
            user.username = user.first_name + " " + user.last_name
            print("user = ", user, user.pk)

            current_site = get_current_site(request)
            subject = 'Please Activate Your Password Reset'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            message = render_to_string('activation_restore_password.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })
            print("uid=", uid, "; token=", token)
            email_user(user, subject, message)

            messages.success(
                request, ('Please check your email for verification'))

            return redirect('activation_sent')
        else:
            print("Invalid")
    else:
        form = RequestRestorePasswordForm()

    return render(request, 'vendor/request_restore_password.html', {'form': form})


def restore_password(request):
    if request.method == 'POST':
        form = RestorePasswordForm(request.POST)

        if form.is_valid():
            user = User.objects.filter(email=form.cleaned_data.get('email')).first()
            if user.password == "":
                user.set_password(form.cleaned_data.get('password1'))
                user.save()
                messages.success(request, ('Your password have been reseted.'))
            else:
                messages.warning(request, ("Your password can't be changed. Please check your email."))
        return redirect('login')
    else:
        form = RestorePasswordForm()

    return render(request, 'vendor/restore_password.html', {'form': form})