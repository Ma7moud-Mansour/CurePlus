# Generated manually for the initial CurePlus order flow.

import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="اسم الاداة")),
                ("description", models.TextField(blank=True, null=True, verbose_name="الوصف")),
                ("price", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="السعر بالجنيه")),
                ("stock", models.PositiveIntegerField(default=0, verbose_name="الكمية المتاحة")),
            ],
            options={
                "verbose_name": "منتج",
                "verbose_name_plural": "المنتجات",
            },
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("customer_name", models.CharField(max_length=255, verbose_name="اسم الطالب")),
                ("customer_mobile", models.CharField(max_length=15, verbose_name="رقم الهاتف")),
                ("customer_email", models.EmailField(max_length=254, verbose_name="البريد الالكتروني")),
                ("college_type", models.CharField(choices=[("government", "حكومي"), ("private", "اهلية")], default="government", max_length=20, verbose_name="نوع الكلية")),
                ("includes_lab_coat", models.BooleanField(default=False, verbose_name="يشمل لاب كوت")),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="اجمالي المبلغ")),
                ("paymob_order_id", models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name="رقم الطلب في Paymob")),
                ("bill_reference", models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name="كود الدفع")),
                ("status", models.CharField(choices=[("PENDING", "معلق في انتظار الدفع"), ("PAID", "تم الدفع بنجاح"), ("FAILED", "فشلت عملية الدفع")], default="PENDING", max_length=20, verbose_name="حالة الطلب")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="تاريخ الانشاء")),
                ("paid_at", models.DateTimeField(blank=True, null=True, verbose_name="تاريخ الدفع")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="mainapp.product", verbose_name="الادوات المحجوزة")),
            ],
            options={
                "verbose_name": "طلب",
                "verbose_name_plural": "الطلبات",
            },
        ),
    ]
