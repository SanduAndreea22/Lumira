from django.db import migrations


CONCERNS = [
    ("hydration", "Hydration", "Hyaluronic acid", "droplet", 0),
    ("radiance", "Radiance", "Vitamin C / niacinamide", "sparkle", 1),
    ("blemishes", "Blemishes", "Salicylic acid", "target", 2),
    ("aging", "Signs of aging", "Retinol (evening)", "clock", 3),
    ("sensitivity", "Sensitivity", "Centella / ceramides", "shield", 4),
    ("oiliness", "Oiliness", "Niacinamide / clay", "leaf", 5),
]

SKIN_TYPES = [
    ("dry", "Dry", 0),
    ("oily", "Oily", 1),
    ("combination", "Combination", 2),
    ("normal", "Normal", 3),
    ("sensitive", "Sensitive", 4),
]

# name, category, step_time, skin_type_slugs, concern_slugs, description
PRODUCTS = [
    ("Gentle Gel Cleanser", "cleanser", "both", [], [], "A soap-free daily cleanser that doesn't strip your skin."),
    ("Creamy Milk Cleanser", "cleanser", "both", ["dry", "sensitive"], [], "A richer, non-foaming cleanser for drier or reactive skin."),

    ("Hyaluronic Acid Serum", "serum", "am", [], ["hydration"], "Multi-weight hyaluronic acid for all-day hydration."),
    ("Vitamin C Brightening Serum", "serum", "am", [], ["radiance"], "Stabilized vitamin C to even out tone and add glow."),
    ("Niacinamide Pore Serum", "serum", "am", [], ["blemishes", "oiliness"], "Niacinamide to refine pores and calm breakouts."),
    ("Centella Calming Serum", "serum", "am", [], ["sensitivity"], "Centella asiatica to soothe redness and reactivity."),
    ("Peptide Firming Serum", "serum", "am", [], ["aging"], "Peptides to support skin ahead of your evening retinol step."),

    ("Lightweight Gel Moisturizer", "moisturizer", "am", ["oily", "combination"], [], "Oil-free gel-cream that hydrates without heaviness."),
    ("Rich Comfort Cream", "moisturizer", "am", ["dry", "sensitive"], [], "A cushiony cream for skin that needs extra comfort."),
    ("Balanced Day Cream", "moisturizer", "am", ["normal"], [], "An easy, everyday moisturizer for balanced skin."),

    ("SPF 30 Everyday Fluid", "spf", "am", [], [], "A lightweight, no-white-cast sunscreen for daily wear."),

    ("Salicylic Acid Treatment", "treatment", "pm", [], ["blemishes"], "BHA exfoliation to keep pores clear overnight."),
    ("Retinol Night Serum", "treatment", "pm", [], ["aging"], "A gentle-strength retinol to support cell turnover while you sleep."),
    ("Niacinamide + Clay Treatment", "treatment", "pm", [], ["oiliness"], "Niacinamide and clay to balance excess oil overnight."),
    ("Centella Ceramide Treatment", "treatment", "pm", [], ["sensitivity"], "Ceramides and centella to repair the skin barrier."),
    ("Hyaluronic Acid Night Serum", "treatment", "pm", [], ["hydration"], "A deeper dose of hyaluronic acid for overnight hydration."),
    ("Niacinamide Brightening Treatment", "treatment", "pm", [], ["radiance"], "Niacinamide overnight to support an even tone."),

    ("Repair Night Cream", "night_cream", "pm", ["dry", "sensitive"], [], "A rich, barrier-repairing night cream."),
    ("Light Night Gel-Cream", "night_cream", "pm", ["oily", "combination"], [], "A breathable gel-cream that won't feel heavy overnight."),
    ("Balanced Night Cream", "night_cream", "pm", ["normal"], [], "A comfortable, everyday night cream."),

    ("Weekly AHA/BHA Exfoliant", "exfoliant", "pm", [], [], "A weekly-strength acid exfoliant for more experienced routines."),
]


def seed_data(apps, schema_editor):
    Concern = apps.get_model("routines", "Concern")
    SkinType = apps.get_model("routines", "SkinType")
    Product = apps.get_model("routines", "Product")

    concern_by_slug = {}
    for slug, name, key_ingredient, icon, order in CONCERNS:
        concern_by_slug[slug] = Concern.objects.create(
            slug=slug, name=name, key_ingredient=key_ingredient, icon=icon, order=order
        )

    skin_type_by_slug = {}
    for slug, name, order in SKIN_TYPES:
        skin_type_by_slug[slug] = SkinType.objects.create(slug=slug, name=name, order=order)

    for name, category, step_time, skin_slugs, concern_slugs, description in PRODUCTS:
        product = Product.objects.create(
            name=name,
            category=category,
            step_time=step_time,
            description=description,
        )
        if skin_slugs:
            product.skin_types.set(skin_type_by_slug[s] for s in skin_slugs)
        if concern_slugs:
            product.concerns.set(concern_by_slug[s] for s in concern_slugs)


def unseed_data(apps, schema_editor):
    apps.get_model("routines", "Product").objects.all().delete()
    apps.get_model("routines", "Concern").objects.all().delete()
    apps.get_model("routines", "SkinType").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("routines", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_data, unseed_data),
    ]
