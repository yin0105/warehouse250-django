from apps.product.models import Category, SubCategory, SubSubCategory


def menu_categories(request):
    categories = Category.objects.all()
    for category in categories:
        subcategories = SubCategory.objects.filter(category=category)
        print("subcategory = ", subcategories)
        for subcategory in subcategories:
            subsubcategories = SubSubCategory.objects.filter(sub_category = subcategory)
            if len(subsubcategories) > 0:
                subcategory.children = subsubcategories
                subcategory.has_children = True
            else:
                subcategory.has_children = False
        if len(subcategories) > 0:
            category.children = subcategories
            category.has_children = True
        else:
            category.has_children = False
    for category in categories:
        print("category = ", category)
        
        if category.has_children:
            for subcategory in category.children:
                print("child: ", subcategory)

                if subcategory.has_children:
                    for subsubcategory in subcategory.children:
                        print("grandchild: ", subsubcategory)
    return {'menu_categories': categories}
