"""Views, split by area — re-exported here so `from . import views` in
urls.py keeps working unchanged (`views.home`, `views.checkout`, etc.).
"""

from .account import my_routines, routine_detail, signup
from .cart import add_routine_to_cart, add_to_cart, cart_view, remove_from_cart_view
from .catalog import product_catalog, product_detail
from .checkout import checkout, checkout_cancel, checkout_success, stripe_webhook
from .pages import about, contact, home
from .quiz import diagnostic_step, redo_diagnostic, routine_result, save_routine

__all__ = [
    "about",
    "add_routine_to_cart",
    "add_to_cart",
    "cart_view",
    "checkout",
    "checkout_cancel",
    "checkout_success",
    "contact",
    "diagnostic_step",
    "home",
    "my_routines",
    "product_catalog",
    "product_detail",
    "redo_diagnostic",
    "remove_from_cart_view",
    "routine_detail",
    "routine_result",
    "save_routine",
    "signup",
    "stripe_webhook",
]
