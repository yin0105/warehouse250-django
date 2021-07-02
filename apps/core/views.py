from django.shortcuts import render

from apps.product.models import Product, Category, SubCategory, SubSubCategory


def frontpage(request):
    newest_products = Product.objects.filter(
        parent=None)[0:4]
    featured_products = Product.objects.filter(is_featured=True)[0:4]
    featured_categories = Category.objects.filter(is_featured=True)
    featured_categories_products = []
    for category in featured_categories:
        for sub_category in SubCategory.objects.filter(category=category):
            for subsubcategory in SubSubCategory.objects.filter(sub_category=sub_category):
                for product in Product.objects.filter(category=subsubcategory):
                    if product.vendor.enabled and product.visible:
                        if len(featured_categories_products) == 4: break
                        featured_categories_products.append(product)
                        

    popular_products = Product.objects.all().order_by('-num_visits')[0:4]
    recently_viewed_products = Product.objects.all().order_by(
        '-last_visit')[0:4]

    return render(request, 'core/frontpage.html', {'newest_products': newest_products, 'featured_products': featured_products, 'featured_categories': featured_categories, 'popular_products': popular_products, 'recently_viewed_products': recently_viewed_products, 'featured_categories_products': featured_categories_products})


def contact(request):
    return render(request, 'core/contact.html')


def about(request):
    return render(request, 'core/about.html')


def pricing(request):
    return render(request, 'core/pricing.html')
