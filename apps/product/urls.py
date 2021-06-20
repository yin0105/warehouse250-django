from django.urls import path

from . import views

urlpatterns = [
    path('search/', views.search, name='search'),
    path('<slug:category_slug>/<slug:subcategory_slug>/<slug:subsubcategory_slug>/<slug:product_slug>/', views.product, name='product'),    
    path('<slug:category_slug>/', views.category, name='category'),
    path('<slug:category_slug>/<slug:subcategory_slug>/', views.subcategory, name='subcategory'),
    path('<slug:category_slug>/<slug:subcategory_slug>/<slug:subsubcategory_slug>/', views.subsubcategory, name='subsubcategory'),
]
