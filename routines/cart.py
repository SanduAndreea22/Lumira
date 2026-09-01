"""Session-backed shopping cart: {product_id (str): quantity}.

Kept out of the database on purpose — a cart is throwaway state until it
becomes an Order at checkout, so there's nothing here worth persisting or
querying outside of the owning session.
"""

from .models import Product

CART_SESSION_KEY = "cart"


def _cart_dict(request):
    return request.session.setdefault(CART_SESSION_KEY, {})


def add(request, product_id):
    cart = _cart_dict(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    request.session.modified = True


def remove(request, product_id):
    cart = _cart_dict(request)
    cart.pop(str(product_id), None)
    request.session.modified = True


def clear(request):
    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True


def get_items(request):
    cart = _cart_dict(request)
    if not cart:
        return []
    products = Product.objects.filter(pk__in=cart.keys(), is_active=True)
    items = []
    for product in products:
        quantity = cart[str(product.pk)]
        items.append(
            {"product": product, "quantity": quantity, "subtotal": product.price * quantity}
        )
    return items


def get_total(request):
    return sum((item["subtotal"] for item in get_items(request)), start=0)


def get_count(request):
    return sum(item["quantity"] for item in get_items(request))
