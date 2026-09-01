from decimal import Decimal

from django.db import migrations

# Fictive demo pricing (USD) — this is a portfolio brand, not a real store.
PRICES = {
    "Gentle Gel Cleanser": "16.00",
    "Creamy Milk Cleanser": "18.00",
    "Hyaluronic Acid Serum": "24.00",
    "Vitamin C Brightening Serum": "32.00",
    "Niacinamide Pore Serum": "22.00",
    "Centella Calming Serum": "26.00",
    "Peptide Firming Serum": "34.00",
    "Lightweight Gel Moisturizer": "20.00",
    "Rich Comfort Cream": "26.00",
    "Balanced Day Cream": "22.00",
    "SPF 30 Everyday Fluid": "19.00",
    "Salicylic Acid Treatment": "24.00",
    "Retinol Night Serum": "34.00",
    "Niacinamide + Clay Treatment": "23.00",
    "Centella Ceramide Treatment": "27.00",
    "Hyaluronic Acid Night Serum": "25.00",
    "Niacinamide Brightening Treatment": "28.00",
    "Repair Night Cream": "32.00",
    "Light Night Gel-Cream": "28.00",
    "Balanced Night Cream": "29.00",
    "Weekly AHA/BHA Exfoliant": "30.00",
}


def set_prices(apps, schema_editor):
    Product = apps.get_model("routines", "Product")
    for name, price in PRICES.items():
        Product.objects.filter(name=name).update(price=Decimal(price))


def unset_prices(apps, schema_editor):
    Product = apps.get_model("routines", "Product")
    Product.objects.filter(name__in=PRICES.keys()).update(price=Decimal("0"))


class Migration(migrations.Migration):

    dependencies = [
        ("routines", "0003_remove_product_brand"),
    ]

    operations = [
        migrations.RunPython(set_prices, unset_prices),
    ]
