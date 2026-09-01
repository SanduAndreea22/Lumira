"""Turns a DiagnosticResult into a concrete Routine + RoutineSteps.

Mapping rules (see docs/brand-brief.md, section 4-5):
- the main concern picks the key ingredient / product for the treatment step
- skin type filters product texture within each category
- experience level decides how many steps the routine gets
"""

from dataclasses import dataclass

from .models import DiagnosticResult, Product, Routine, RoutineStep

AM = RoutineStep.TimeOfDay.AM
PM = RoutineStep.TimeOfDay.PM

# category, reason template) per time of day, keyed by experience level
_PLAN = {
    DiagnosticResult.Experience.BEGINNER: {
        AM: [Product.Category.CLEANSER, Product.Category.MOISTURIZER, Product.Category.SPF],
        PM: [Product.Category.CLEANSER, Product.Category.NIGHT_CREAM],
    },
    DiagnosticResult.Experience.SOME_ROUTINE: {
        AM: [
            Product.Category.CLEANSER,
            Product.Category.SERUM,
            Product.Category.MOISTURIZER,
            Product.Category.SPF,
        ],
        PM: [Product.Category.CLEANSER, Product.Category.TREATMENT, Product.Category.NIGHT_CREAM],
    },
    DiagnosticResult.Experience.ADVANCED: {
        AM: [
            Product.Category.CLEANSER,
            Product.Category.SERUM,
            Product.Category.MOISTURIZER,
            Product.Category.SPF,
        ],
        PM: [
            Product.Category.CLEANSER,
            Product.Category.EXFOLIANT,
            Product.Category.TREATMENT,
            Product.Category.NIGHT_CREAM,
        ],
    },
}

_REASONS = {
    Product.Category.CLEANSER: "Gently clears the canvas without stripping your skin.",
    Product.Category.SERUM: "Targets {concern} with {ingredient}, right after cleansing.",
    Product.Category.MOISTURIZER: "Locks in hydration for your {skin_type} skin.",
    Product.Category.SPF: "Protects what the rest of the routine builds.",
    Product.Category.TREATMENT: "Your main active for {concern}: {ingredient}.",
    Product.Category.NIGHT_CREAM: "Richer texture to support repair while you sleep.",
    Product.Category.EXFOLIANT: "A weekly-strength step to keep {concern} in check.",
}


@dataclass
class StepPlan:
    time_of_day: str
    order: int
    category: str
    product: Product
    reason: str


class NoProductAvailable(Exception):
    """Raised when the catalog has no product for a required step."""


def _pick_product(category, result: DiagnosticResult) -> Product:
    qs = Product.objects.filter(category=category, is_active=True)
    qs = qs.filter(skin_types=result.skin_type) | qs.filter(skin_types__isnull=True)
    concern_relevant = category in (
        Product.Category.SERUM,
        Product.Category.TREATMENT,
        Product.Category.EXFOLIANT,
    )
    if concern_relevant:
        with_concern = qs.filter(concerns=result.concern)
        if with_concern.exists():
            qs = with_concern
    product = qs.distinct().first()
    if product is None:
        raise NoProductAvailable(
            f"No active '{category}' product found for {result.skin_type} / {result.concern}."
        )
    return product


def build_routine(result: DiagnosticResult, *, user=None, save: bool = True) -> Routine:
    """Build (and optionally persist) a Routine + RoutineSteps for a diagnostic result."""

    plan = _PLAN[result.experience]
    steps: list[StepPlan] = []
    for time_of_day, categories in plan.items():
        for order, category in enumerate(categories, start=1):
            product = _pick_product(category, result)
            reason = _REASONS[category].format(
                concern=result.concern.name.lower(),
                ingredient=result.concern.key_ingredient,
                skin_type=result.skin_type.name.lower(),
            )
            steps.append(StepPlan(time_of_day, order, category, product, reason))

    if not save:
        return steps  # type: ignore[return-value]

    routine = Routine.objects.create(user=user, diagnostic_result=result)
    RoutineStep.objects.bulk_create(
        [
            RoutineStep(
                routine=routine,
                time_of_day=step.time_of_day,
                order=step.order,
                product=step.product,
                reason=step.reason,
            )
            for step in steps
        ]
    )
    return routine
