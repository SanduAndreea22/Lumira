from django.shortcuts import get_object_or_404, render

from ..models import Concern, Product, SkinType


def product_catalog(request):
    products = Product.objects.filter(is_active=True).prefetch_related("concerns", "skin_types")
    concern_slug = request.GET.get("concern") or ""
    skin_slug = request.GET.get("skin_type") or ""
    if concern_slug:
        products = products.filter(concerns__slug=concern_slug)
    if skin_slug:
        products = products.filter(skin_types__slug=skin_slug)
    return render(
        request,
        "routines/products.html",
        {
            "products": products.distinct(),
            "concerns": Concern.objects.all(),
            "skin_types": SkinType.objects.all(),
            "selected_concern": concern_slug,
            "selected_skin_type": skin_slug,
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related("concerns", "skin_types"), pk=pk, is_active=True
    )
    return render(request, "routines/product_detail.html", {"product": product})
