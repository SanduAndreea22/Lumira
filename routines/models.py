from django.conf import settings
from django.db import models


class Concern(models.Model):
    """A primary skin concern the diagnostic can address (e.g. hydration)."""

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200, blank=True)
    key_ingredient = models.CharField(
        max_length=120,
        help_text="Headline active ingredient used to explain the treatment step, e.g. 'Hyaluronic acid'.",
    )
    ingredient_explanation = models.CharField(
        max_length=240,
        blank=True,
        help_text="One-sentence, jargon-free explanation of why the key ingredient works.",
    )
    icon = models.CharField(
        max_length=40,
        blank=True,
        help_text="Name of a stroke icon used in the UI (e.g. 'droplet').",
    )
    accent_color = models.CharField(
        max_length=7,
        default="#c2486b",
        help_text="Hex accent color used to give this concern's routines a distinct identity.",
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class SkinType(models.Model):
    """Skin type used to filter product texture (dry/oily/combination/...)."""

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=40)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    # Private-label brand: every product in the catalog is Lumira's own, so
    # there's deliberately no external "brand" field to fill in.
    class Category(models.TextChoices):
        CLEANSER = "cleanser", "Cleanser"
        SERUM = "serum", "Treatment serum"
        MOISTURIZER = "moisturizer", "Moisturizer"
        SPF = "spf", "SPF"
        TREATMENT = "treatment", "Active treatment"
        NIGHT_CREAM = "night_cream", "Night cream"
        EXFOLIANT = "exfoliant", "Exfoliant"

    class StepTime(models.TextChoices):
        AM = "am", "Morning"
        PM = "pm", "Evening"
        BOTH = "both", "Morning & evening"

    name = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=Category.choices)
    step_time = models.CharField(max_length=4, choices=StepTime.choices, default=StepTime.BOTH)
    description = models.TextField(blank=True)
    concerns = models.ManyToManyField(Concern, related_name="products", blank=True)
    skin_types = models.ManyToManyField(SkinType, related_name="products", blank=True)
    is_fragrance_free = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class DiagnosticResult(models.Model):
    class Experience(models.TextChoices):
        BEGINNER = "beginner", "Just starting out"
        SOME_ROUTINE = "some_routine", "I already have a routine"
        ADVANCED = "advanced", "Advanced"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="diagnostic_results",
        null=True,
        blank=True,
    )
    concern = models.ForeignKey(Concern, on_delete=models.PROTECT, related_name="+")
    skin_type = models.ForeignKey(SkinType, on_delete=models.PROTECT, related_name="+")
    experience = models.CharField(max_length=20, choices=Experience.choices)
    wants_fragrance_free = models.BooleanField(default=False)
    wants_vegan = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.concern} / {self.skin_type} ({self.created_at:%Y-%m-%d})"


class Routine(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="routines",
        null=True,
        blank=True,
    )
    diagnostic_result = models.ForeignKey(
        DiagnosticResult, on_delete=models.CASCADE, related_name="routines"
    )
    name = models.CharField(max_length=120, blank=True)
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name or f"Routine #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"{self.diagnostic_result.concern.name} routine"
        super().save(*args, **kwargs)
        if self.is_current and self.user_id:
            Routine.objects.filter(user_id=self.user_id, is_current=True).exclude(
                pk=self.pk
            ).update(is_current=False)


class RoutineStep(models.Model):
    class TimeOfDay(models.TextChoices):
        AM = "am", "Morning"
        PM = "pm", "Evening"

    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name="steps")
    time_of_day = models.CharField(max_length=2, choices=TimeOfDay.choices)
    order = models.PositiveSmallIntegerField()
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="+")
    reason = models.CharField(max_length=200)

    class Meta:
        ordering = ["time_of_day", "order"]

    def __str__(self):
        return f"{self.time_of_day.upper()} #{self.order}: {self.product.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    default_skin_type = models.ForeignKey(
        SkinType, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    stripe_checkout_session_id = models.CharField(max_length=200, unique=True)
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="+")
    quantity = models.PositiveSmallIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class ContactMessage(models.Model):
    class Subject(models.TextChoices):
        ORDER = "order", "An order"
        PRODUCT = "product", "A product question"
        OTHER = "other", "Something else"

    subject = models.CharField(max_length=20, choices=Subject.choices, default=Subject.OTHER)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"
