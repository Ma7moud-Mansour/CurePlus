from decimal import Decimal

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.crypto import get_random_string

from mainapp.models import Order, PricingSettings, Product


def money_as_int(value):
    return int(value) if value == value.to_integral_value() else float(value)


def calculate_total(pricing, college_type, includes_lab_coat):
    total = pricing.base_box_price
    if college_type == "private":
        total += pricing.private_college_extra
    if includes_lab_coat:
        total += pricing.lab_coat_price
    return total


def home(request):
    pricing = PricingSettings.load()

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        email = request.POST.get("email", "").strip()
        college_type = request.POST.get("college_type", "government")
        includes_lab_coat = request.POST.get("lab_coat") == "yes"

        if college_type not in {"government", "private"}:
            college_type = "government"

        if not name or not mobile or not email:
            messages.error(request, "من فضلك اكتب الاسم ورقم الهاتف والبريد الالكتروني.")
            return redirect("home")

        product, _created = Product.objects.get_or_create(
            name="بوكس 2nd Year Dent Zag الاساسي",
            defaults={
                "description": "Torch, Dental Knife, Dental Carver, Napkins, Blue Wax, Socks",
                "price": pricing.base_box_price,
                "stock": 0,
            },
        )
        if product.price != pricing.base_box_price:
            product.price = pricing.base_box_price
            product.save(update_fields=["price"])

        order = Order.objects.create(
            customer_name=name,
            customer_mobile=mobile,
            customer_email=email,
            college_type=college_type,
            includes_lab_coat=includes_lab_coat,
            product=product,
            total_amount=calculate_total(pricing, college_type, includes_lab_coat),
            bill_reference=get_random_string(10).upper(),
        )
        messages.success(request, f"تم تسجيل طلبك بنجاح. رقم الطلب: {order.bill_reference}")
        return redirect("home")

    context = {
        "base_box_price": money_as_int(pricing.base_box_price),
        "private_college_extra": money_as_int(pricing.private_college_extra),
        "lab_coat_price": money_as_int(pricing.lab_coat_price),
        "equipment": [
            ("Torch", "https://lh3.googleusercontent.com/aida-public/AB6AXuC8k6iy9aEBe1Y-Vsg8RsN2rYkHqWHT80L70bdDypdyr9eg3BS1V1kz5a9Pl4qT3cCMrKxH2w2f6sYI0kdSB_PkPCMNtQAP6p9YPoG9USfcFsGLPsCc3ynhQkro92ahhTE6fjWFO1K5V4EZ-0NqXa-wyD0uZDqVier_Q5EKmAyZk_eoYqkMnQGleo1AyTCDHF0aq_qIXZqk4RofI4Siqz1MKOqihYaL_qiCeDiSvj7AhOuyOVaRqMshb2EnpLOt6GVn-bYLmNGkSQ"),
            ("Dental Knife", "https://lh3.googleusercontent.com/aida-public/AB6AXuDcgTD1LQm12sySAeNAGqQxou1UGG3VMLIRpL2rTe5r8e3XahOkssV6sJ1QRFci9rhm8Qn5UJCrPSgYfJcLYE5RJvsVH58cwJ_YM-mwbqpY2T5kGpcOl3Zj6Qcyq5dR1G_swfwnmVTDt2R-W1qNpmG7ZdaFacT7NFTcCbJym4m8ZilewLCVW0J4hrubExWaMcsk3PEw3eyzEeQEq25iLSOhAc9Y-6svCIDkQbbDMkssfmdZxAvFtmC5FvhkkFSSlFtEj2rtUje9mw"),
            ("Dental Carver", "https://lh3.googleusercontent.com/aida-public/AB6AXuA48ejpwkzttP5-nweNwc3DHSrRhV01X2UxHn7iULz-COMM-2w1YqNZgk5Ny4_dRSY4MG6LdjNpUv3_lTOBhse7xbmflpu0frlVZWrC2l7YV81m8c3Y-qPSqYmOVt5ADEnvMh22Ip6a8fe-1qtsSggCBIL5sEnSq68hoNf4aTunPqTU7VHgDOO7eU00ZYnBFm_YlPQeHQgdw3MIcqqoCPJ5yIQgPnJHg5FiZnF1eI7UzXKgHFIa62BkOD9-W96ijPp5Y4iVqFzkMQ"),
            ("Napkins", "https://lh3.googleusercontent.com/aida-public/AB6AXuDF03Zcx3_saRGQA2rZGgA5zqmJZqNh1-H062mkb0DTL73bvPGJM3acGuCgFz3dyKGJ9NJeQIOLrEs_CiKg_NpAx6xJOzsYdcRoNkakxOMWW3pQU8Ua8HCOqNxPSXBaMtGQiL-ZhGiMD7w3Xl16irS4y-7iiVeiKeBDXGhabAxi9xlfs1JuXpUJvCIkrhLN54yjvLIhzoRwoGNhsLCPw9v00WsjLDsSnwUDOJQLzWl-yGRpRw_kh5F7I0somJxTg91p5JXYu_b1Kw"),
            ("Blue Wax", "https://lh3.googleusercontent.com/aida-public/AB6AXuD-wPrVo1cwz065AcmR1aqHtuq_E2DmByHFnnJw7aEeYAj0aFsxgq9UUYNJdRSzdERfltLiYruP73Bp8iomTh4mQt_dNUgRwqdMwc6y3o2o-h1a3o75kQ6JZWuC80NXAcW5QZV3wSC96hgTO-Cz6Nvl6pp8uAdvTVBotA6CYnygj5kZS5o4KE6cah2tmBjpP2k2coUjydiAQps_DkZ-hkIGK99T0dDIcvUbzVwIX_PPpY6p3bbVDtONYKcvQ2xZouuxP9b1vBSZzA"),
            ("Socks", "https://lh3.googleusercontent.com/aida-public/AB6AXuCIym7-wZ_kswnk_UhodkIa5V-S-Ccj9te50k7C3ulW2F4kI9ST-FZdbp27Jo4A5L_bEiZgkLtonmj1y51oUeMmRR30G7ltAByod0zGxJ9-62kfAiAmbluwEr6XWMjDiaoIwLyTPB_J3Qa4N_OJRVFlAXZW32BmQSKG27km5-PW8kzB5KUNgxI8DNwzVJpmZYbj2eeG8Y9KBEkqTNtiVVvCObYg7mVVkuWbhJGmxwXlW3QimUKe5zA16Vd_Q02FIJAAR5m8TnQ-lA"),
        ],
    }
    return render(request, "mainapp/home.html", context)
