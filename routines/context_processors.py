from . import cart as cart_utils


def cart(request):
    # Every real request has a session (SessionMiddleware runs before any
    # view), but this context processor also fires while rendering error
    # pages — be defensive rather than let a request without one 500.
    if not hasattr(request, "session"):
        return {"cart_count": 0}
    return {"cart_count": cart_utils.get_count(request)}
