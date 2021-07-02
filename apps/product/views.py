import random

from datetime import datetime

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from .forms import AddToCartForm, AddToCartInListForm
from .models import Category, ProductImage, SubCategory, SubSubCategory, Product

from apps.cart.cart import Cart


def search(request):
    query = request.GET.get('query', '')
    instock = request.GET.get('instock')
    price_from = request.GET.get('price_from', 0)
    price_to = request.GET.get('price_to', 5000000)
    sorting = request.GET.get('sorting', '-date_added')
    products = Product.objects.filter(Q(title__icontains=query) | Q(
        description__icontains=query)).filter(price__gte=price_from).filter(price__lte=price_to)

    if instock:
        products = products.filter(num_available__gte=1)

    return render(request, 'product/search.html', {'products': products.order_by(sorting), 'query': query, 'instock': instock, 'price_from': price_from, 'price_to': price_to, 'sorting': sorting})


def product(request, category_slug, subcategory_slug, subsubcategory_slug, product_slug):
    cart = Cart(request)

    product = get_object_or_404(
        Product, category__slug=subsubcategory_slug, slug=product_slug, visible=True, vendor__enabled=True)
    product.num_visits = product.num_visits + 1
    product.last_visit = datetime.now()
    product.save()

    if request.method == 'POST':
        form = AddToCartForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data['quantity']

            cart.add(product_id=product.id,
                     quantity=quantity, update_quantity=False)

            messages.success(request, 'The product was added to the cart')

            return redirect('product', category_slug=category_slug, subcategory_slug=subcategory_slug, subsubcategory_slug=subsubcategory_slug, product_slug=product_slug)
    else:
        form = AddToCartForm()

    similar_products = list(product.category.products.exclude(id=product.id))

    if len(similar_products) >= 4:
        similar_products = random.sample(similar_products, 4)

    cart = Cart(request)

    if cart.has_product(product.id):
        product.in_cart = True
    else:
        product.in_cart = False
    product_imgs = ProductImage.objects.filter(product=product)

    return render(request, 'product/product.html', {'form': form, 'product': product, 'imgs': product_imgs, 'similar_products': similar_products})


def category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(visible=True)

    if request.method == 'POST':
        cart = Cart(request)

        form = AddToCartInListForm(request.POST)
        
        if form.is_valid():
            product_slug = form.cleaned_data['slug']
        
            product = get_object_or_404(
                Product, category__sub_category__category__slug=category_slug, slug=product_slug)
            product.num_visits = product.num_visits + 1
            product.last_visit = datetime.now()
            product.save()
            
            cart.add(product_id=product.id, quantity=1, update_quantity=False)

            messages.success(request, 'The product was added to the cart')

            return redirect('category', category_slug=category_slug)

    return render(request, 'product/category.html', {'category': category, 'products': products})

def subcategory(request, category_slug, subcategory_slug):
    category = get_object_or_404(SubCategory, slug=subcategory_slug)
    products = Product.objects.filter(visible=True)

    if request.method == 'POST':
        cart = Cart(request)

        form = AddToCartInListForm(request.POST)
        
        if form.is_valid():
            product_slug = form.cleaned_data['slug']
        
            product = get_object_or_404(
                Product, category__sub_category__slug=subcategory_slug, slug=product_slug)
            product.num_visits = product.num_visits + 1
            product.last_visit = datetime.now()
            product.save()
            
            cart.add(product_id=product.id, quantity=1, update_quantity=False)

            messages.success(request, 'The product was added to the cart')

            return redirect('subcategory', category_slug=category_slug, subcategory_slug=subcategory_slug)

    return render(request, 'product/subcategory.html', {'category': category, 'products': products})


def subsubcategory(request, category_slug, subcategory_slug, subsubcategory_slug):
    category = get_object_or_404(SubSubCategory, slug=subsubcategory_slug)
    products = Product.objects.filter(visible=True)

    if request.method == 'POST':
        cart = Cart(request)

        form = AddToCartInListForm(request.POST)
        
        if form.is_valid():
            product_slug = form.cleaned_data['slug']
        
            product = get_object_or_404(
                Product, category__slug=subsubcategory_slug, slug=product_slug)
            product.num_visits = product.num_visits + 1
            product.last_visit = datetime.now()
            product.save()
            
            cart.add(product_id=product.id, quantity=1, update_quantity=False)

            messages.success(request, 'The product was added to the cart')

            return redirect('subsubcategory', category_slug=category_slug, subcategory_slug=subcategory_slug, subsubcategory_slug=subsubcategory_slug)

    return render(request, 'product/subsubcategory.html', {'category': category, 'products': products})

