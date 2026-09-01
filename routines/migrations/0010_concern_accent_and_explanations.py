from django.db import migrations

DATA = {
    "hydration": {
        "explanation": "Hyaluronic acid holds up to 1000x its weight in water, pulling moisture into skin.",
        "accent_color": "#5FB8DB",
    },
    "radiance": {
        "explanation": "Vitamin C and niacinamide both help fade dark spots and even out tone over time.",
        "accent_color": "#E3A93F",
    },
    "blemishes": {
        "explanation": "Salicylic acid dissolves the oil and buildup inside pores that leads to breakouts.",
        "accent_color": "#E0736E",
    },
    "aging": {
        "explanation": "Retinol speeds up cell turnover, which softens fine lines and fades uneven texture.",
        "accent_color": "#8B7FD1",
    },
    "sensitivity": {
        "explanation": "Centella calms visible redness while ceramides rebuild the skin barrier that keeps irritants out.",
        "accent_color": "#7FC29B",
    },
    "oiliness": {
        "explanation": "Niacinamide helps regulate oil production, while clay lifts excess shine without over-drying.",
        "accent_color": "#4FA89B",
    },
}


def set_data(apps, schema_editor):
    Concern = apps.get_model("routines", "Concern")
    for slug, values in DATA.items():
        Concern.objects.filter(slug=slug).update(
            ingredient_explanation=values["explanation"], accent_color=values["accent_color"]
        )


def unset_data(apps, schema_editor):
    Concern = apps.get_model("routines", "Concern")
    Concern.objects.filter(slug__in=DATA.keys()).update(ingredient_explanation="", accent_color="#c2486b")


class Migration(migrations.Migration):

    dependencies = [
        ("routines", "0009_concern_accent_color_concern_ingredient_explanation"),
    ]

    operations = [
        migrations.RunPython(set_data, unset_data),
    ]
