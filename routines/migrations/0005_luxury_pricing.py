from decimal import Decimal

from django.db import migrations

# Repositioned to a luxury/premium price point (see docs/brand-brief.md,
# section 2: target audience is all ages, luxury budget).
PRICES = {
    "Gentle Gel Cleanser": "38.00",
    "Creamy Milk Cleanser": "42.00",
    "Hyaluronic Acid Serum": "58.00",
    "Vitamin C Brightening Serum": "78.00",
    "Niacinamide Pore Serum": "54.00",
    "Centella Calming Serum": "62.00",
    "Peptide Firming Serum": "85.00",
    "Lightweight Gel Moisturizer": "48.00",
    "Rich Comfort Cream": "62.00",
    "Balanced Day Cream": "52.00",
    "SPF 30 Everyday Fluid": "42.00",
    "Salicylic Acid Treatment": "58.00",
    "Retinol Night Serum": "85.00",
    "Niacinamide + Clay Treatment": "55.00",
    "Centella Ceramide Treatment": "64.00",
    "Hyaluronic Acid Night Serum": "60.00",
    "Niacinamide Brightening Treatment": "68.00",
    "Repair Night Cream": "78.00",
    "Light Night Gel-Cream": "68.00",
    "Balanced Night Cream": "70.00",
    "Weekly AHA/BHA Exfoliant": "72.00",
}

PREVIOUS_PRICES = {
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


def set_luxury_prices(apps, schema_editor):
    Product = apps.get_model("routines", "Product")
    for name, price in PRICES.items():
        Product.objects.filter(name=name).update(price=Decimal(price))


def revert_to_previous_prices(apps, schema_editor):
    Product = apps.get_model("routines", "Product")
    for name, price in PREVIOUS_PRICES.items():
        Product.objects.filter(name=name).update(price=Decimal(price))


class Migration(migrations.Migration):

    dependencies = [
        ("routines", "0004_add_product_prices"),
    ]

    operations = [
        migrations.RunPython(set_luxury_prices, revert_to_previous_prices),
    ]
