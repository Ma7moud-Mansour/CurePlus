import uuid

from django.db import models
from django.utils import timezone


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="اسم الاداة")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر بالجنيه")
    stock = models.PositiveIntegerField(default=0, verbose_name="الكمية المتاحة")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"


class PricingSettings(models.Model):
    base_box_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=600,
        verbose_name="سعر البوكس الاساسي للحكومي",
    )
    private_college_extra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="زيادة الاهلية عن الحكومي",
    )
    lab_coat_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=200,
        verbose_name="سعر اللاب كوت",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="اخر تحديث")

    @classmethod
    def load(cls):
        settings, _created = cls.objects.get_or_create(pk=1)
        return settings

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return None

    def __str__(self):
        return "اعدادات الاسعار"

    class Meta:
        verbose_name = "اعدادات الاسعار"
        verbose_name_plural = "اعدادات الاسعار"


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "معلق في انتظار الدفع"),
        ("PAID", "تم الدفع بنجاح"),
        ("FAILED", "فشلت عملية الدفع"),
    ]
    COLLEGE_TYPE_CHOICES = [
        ("government", "حكومي"),
        ("private", "اهلية"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=255, verbose_name="اسم الطالب")
    customer_mobile = models.CharField(max_length=15, verbose_name="رقم الهاتف")
    customer_email = models.EmailField(verbose_name="البريد الالكتروني")
    college_type = models.CharField(
        max_length=20,
        choices=COLLEGE_TYPE_CHOICES,
        default="government",
        verbose_name="نوع الكلية",
    )
    includes_lab_coat = models.BooleanField(default=False, verbose_name="يشمل لاب كوت")

    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="الادوات المحجوزة")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="اجمالي المبلغ")

    paymob_order_id = models.CharField(max_length=100, blank=True, null=True, db_index=True, verbose_name="رقم الطلب في Paymob")
    bill_reference = models.CharField(max_length=100, blank=True, null=True, db_index=True, verbose_name="كود الدفع")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING", verbose_name="حالة الطلب")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الانشاء")
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="تاريخ الدفع")

    def __str__(self):
        return f"طلب {self.customer_name} - {self.total_amount} جنيه"

    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"
