import stripe

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect

from django.http import JsonResponse

from .cart import Cart
from .forms import CheckoutForm, PaymentForm
from .models import District, Sector, Cell, Village, DeliveryCost

from apps.order.utilities import checkout, notify_customer, notify_vendor

from apps.vendor.models import Vendor, Customer

from apps.order.models import Order


def cart_detail(request):
    cart = Cart(request)

    if request.method == 'POST':
        if request.user.is_authenticated:
            # messages.success(request, 'Thank you for your order')
            if "id_quantity" in request.POST:
                for elem in request.POST["id_quantity"].split(":"):
                    print("== elem = ", elem)
                    elem_id = elem.split("_")[0]
                    elem_quantity = elem.split("_")[1]
                    cart.set(elem_id, elem_quantity)
            return redirect('contact_info')
        else:
            messages.success(request, 'Please sign in')
            return redirect('login')

    remove_from_cart = request.GET.get('remove_from_cart', '')
    change_quantity = request.GET.get('change_quantity', '')
    quantity = request.GET.get('quantity', 0)

    if remove_from_cart:
        cart.remove(remove_from_cart)
        return redirect('cart')

    if change_quantity:
        cart.add(change_quantity, quantity, True)
        return redirect('cart')

    return render(request, 'cart/cart.html')


def contact_info(request):
    cart = Cart(request)

    districts = District.objects.all()
    delivery_costs = DeliveryCost.objects.all()

    cart_vendor = Vendor.objects.filter(email=request.user.email).first()
    cart_customer = Customer.objects.filter(email=request.user.email).first()
    pickup_avaliable = True

    # if cart_vendor:
    #     cart_user = cart_vendor
    # else:
    #     cart_user = cart_customer

    if cart_customer:
        if request.method == 'POST':
            form = CheckoutForm(request.POST)

            if form.is_valid():
                district_id = form.cleaned_data['district']
                sector_id = form.cleaned_data['sector']
                cell_id = form.cleaned_data['cell']
                village_id = form.cleaned_data['village']
                address = form.cleaned_data['delivery_address']
                # cost = form.cleaned_data['delivery_cost']                

                option = form.cleaned_data['delivery_option']

                if option == "Store":
                    district = ''
                    sector = ''
                    cell = ''
                    village = ''
                    cost = '0'
                    address = ''
                else:
                    district = District.objects.get(id=district_id).district
                    sector = Sector.objects.get(id=sector_id).sector
                    cell = Cell.objects.get(id=cell_id).cell
                    village = Village.objects.get(id=village_id).village

                    if option == "Express_Delivery":
                        cost = 10000
                    else:
                        cost = 5000

                cart.add_deliver(district, sector, cell,
                                 village, address, cost)

                return redirect('payment_check')

        else:
            form = CheckoutForm()
            pickup_avaliable = True
            for item in cart:
                if item["product"] and not item["product"].pickup_available:
                    pickup_avaliable = False

    else:
        return redirect('cart')
    return render(request, 'cart/contact.html', {'form': form, 'cart_user': cart_customer, 'districts': districts, 'delivery_costs': delivery_costs, 'pickup_available': pickup_avaliable})


def district_sector(request):
    district_id = request.GET.get('districtId')
    sectors = Sector.objects.filter(district_id=district_id)

    return JsonResponse(list(sectors.values('id', 'sector')), safe=False)


def district_sector_cell(request):
    district_id = request.GET.get('districtId')
    sector_id = request.GET.get('sectorId')
    cells = Cell.objects.filter(district_id=district_id, sector_id=sector_id)

    return JsonResponse(list(cells.values('id', 'cell')), safe=False)


def district_sector_cell_village(request):
    district_id = request.GET.get('districtId')
    sector_id = request.GET.get('sectorId')
    cell_id = request.GET.get('cellId')
    villages = Village.objects.filter(
        district_id=district_id, sector_id=sector_id, cell_id=cell_id)

    return JsonResponse(list(villages.values('id', 'village')), safe=False)


def payment_check(request):
    cart = Cart(request)
    print("================== payment_check")
    if request.method == 'POST':
        form = PaymentForm(request.POST)  # PaymentForm

        if form.is_valid():
            print("== form is valid")
            stripe.api_key = settings.STRIPE_SECRET_KEY

            stripe_token = form.cleaned_data['stripe_token']

            try:
                charge = stripe.Charge.create(
                    amount=int(cart.get_total_cost() * 100),
                    currency='USD',
                    description='Charge from Warehouse250',
                    source=stripe_token
                )

                first_name = request.user.customer.customername.split(' ')[0]
                if len(request.user.customer.customername.split(' ')) > 1:
                    last_name = request.user.customer.customername.split(' ')[1]
                else:
                    last_name = ""
                email = request.user.customer.email
                phone = request.user.customer.phone
                address = request.user.customer.address
                district = cart.cart['delivery']['district']
                sector = cart.cart['delivery']['sector']
                cell = cart.cart['delivery']['cell']
                village = cart.cart['delivery']['village']
                delivery_address = cart.cart['delivery']['address']
                delivery_cost = cart.cart['delivery']['cost']
                order = checkout(request, first_name, last_name, email, address, phone, district,
                                    sector, cell, village, delivery_address, delivery_cost, cart.get_total_cost())

                cart.clear()

                notify_customer(order)
                notify_vendor(order)

                return redirect('success')
            except Exception:
                messages.error(
                    request, 'There was something wrong with the payment')
    else:
        form = PaymentForm()

    return render(request, 'cart/payment.html', {'form': form, 'stripe_pub_key': settings.STRIPE_PUB_KEY})


def success(request):
    return render(request, 'cart/success.html')