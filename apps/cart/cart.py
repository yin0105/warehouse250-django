from django.conf import settings

from apps.product.models import Product


class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    def __iter__(self):
        for p in self.cart.keys():
            if p != 'delivery':
                self.cart[str(p)]['product'] = Product.objects.get(pk=p)

        for item in self.cart.values():
            if 'product' in item:
                item['total_price'] = item['product'].get_discounted_price() * item['quantity']

                yield item

    def __len__(self):
        sum_quantity = 0
        for item in self.cart.values():
            if 'quantity' in item:
                sum_quantity += item['quantity']
        return sum_quantity

    def add(self, product_id, quantity=1, update_quantity=False):
        product_id = str(product_id)

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': quantity, 'id': product_id}

        if update_quantity:
            self.cart[product_id]['quantity'] += int(quantity)

            if self.cart[product_id]['quantity'] == 0:
                self.remove(product_id)

        self.save()

    def set(self, product_id, quantity=1):
        product_id = str(product_id)

        self.cart[product_id]['quantity'] = int(quantity)

        if self.cart[product_id]['quantity'] == 0:
            self.remove(product_id)

        self.save()

    def add_deliver(self, district, sector, cell, village, address, cost):
        self.cart['delivery'] = {'district': district, 'sector': sector, 'cell': cell, 'village': village, 'address': address, 'cost': cost}

        self.save()


    def has_product(self, product_id):
        if str(product_id) in self.cart:
            return True
        else:
            return False

    def remove(self, product_id):
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def get_delivery_cost(self):
        if "delivery" in self.cart:
            print(" delivery - 1")
            if self.cart['delivery']['cost']:
                print(" delivery - 2 *", self.cart['delivery']['cost'], "#")
        if "delivery" in self.cart and self.cart['delivery']['cost']:
            return self.cart['delivery']['cost']
        return 0

    def get_delivery_address(self):
        address = self.cart['delivery']['district'] + ' - ' + self.cart['delivery']['sector'] + ' - ' + self.cart['delivery']['cell'] + ' - ' + self.cart['delivery']['village'] + ' - ' + self.cart['delivery']['address']
        return address

    def get_cart_cost(self):
        for p in self.cart.keys():
            if p != 'delivery':
                self.cart[str(p)]['product'] = Product.objects.get(pk=p)

        total_cost = 0
        for item in self.cart.values():
            if 'product' in item:
                total_cost += item['product'].get_discounted_price() * item['quantity']
        return total_cost

    def get_total_cost(self):
        for p in self.cart.keys():
            if p != 'delivery':
                self.cart[str(p)]['product'] = Product.objects.get(pk=p)

        total_cost = 0
        for item in self.cart.values():
            if 'product' in item:
                total_cost += item['product'].get_discounted_price() * item['quantity']
        
        if "delivery" in self.cart and self.cart['delivery']['cost']:
            total_cost += int(self.cart['delivery']['cost'])
        
        return total_cost
