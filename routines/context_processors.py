from . import cart as cart_utils


def cart(request):
    return {"cart_count": cart_utils.get_count(request)}
