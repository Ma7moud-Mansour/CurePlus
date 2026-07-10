import json
import logging

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt

from mainapp.models import Order, PricingSettings, Product
from mainapp import paymob

logger = logging.getLogger(__name__)


def money_as_int(value):
    return int(value) if value == value.to_integral_value() else float(value)


def calculate_total(pricing, includes_lab_coat):
    total = pricing.base_box_price
    if includes_lab_coat:
        total += pricing.lab_coat_price
    return total


# ── Home / Order Form ──────────────────────────────────────────────


def home(request):
    pricing = PricingSettings.load()

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        email = request.POST.get("email", "").strip()
        includes_lab_coat = request.POST.get("lab_coat") == "yes"

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

        total = calculate_total(pricing, includes_lab_coat)

        order = Order.objects.create(
            customer_name=name,
            customer_mobile=mobile,
            customer_email=email,
            includes_lab_coat=includes_lab_coat,
            product=product,
            total_amount=total,
            bill_reference=get_random_string(10).upper(),
        )

        # ── Paymob Payment Flow ────────────────────────────────────
        try:
            amount_cents = int(total * 100)

            name_parts = name.split(maxsplit=1)
            billing_data = {
                "first_name": name_parts[0],
                "last_name": name_parts[1] if len(name_parts) > 1 else "NA",
                "email": email,
                "phone_number": mobile,
            }

            # Single API call: Create Payment Intention
            result = paymob.create_intention(
                amount_cents=amount_cents,
                billing_data=billing_data,
                merchant_order_id=str(order.id),
            )

            order.paymob_order_id = str(result["intention_id"])
            order.save(update_fields=["paymob_order_id"])

            # Redirect to Paymob Unified Checkout
            return redirect(paymob.build_checkout_url(result["client_secret"]))

        except Exception:
            logger.exception("Paymob payment flow failed for order %s", order.id)
            order.status = "FAILED"
            order.save(update_fields=["status"])
            messages.error(request, "حدث خطأ أثناء تحويلك للدفع. حاول مرة أخرى.")
            return redirect("home")

    context = {
        "base_box_price": money_as_int(pricing.base_box_price),
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


# ── Paymob Webhook (Server-to-Server) ─────────────────────────────


@csrf_exempt
def paymob_webhook(request):
    """
    POST endpoint for Paymob's 'Transaction Processed Callback'.

    Paymob sends a JSON body with the transaction details and an HMAC
    signature. We verify the HMAC, then update the order status.

    URL to configure in Paymob Dashboard:
        https://yourdomain.com/payment/webhook/
    """
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Webhook received invalid JSON body.")
        return HttpResponse(status=400)

    # The HMAC is at the top level of the JSON body
    received_hmac = body.get("hmac", "")
    transaction = body.get("obj", {})

    # Verify HMAC signature
    if not paymob.verify_hmac(transaction, received_hmac):
        logger.warning("Webhook HMAC verification failed.")
        return HttpResponse(status=403)

    # Extract transaction details
    success = transaction.get("success", False)
    is_voided = transaction.get("is_voided", False)
    is_refunded = transaction.get("is_refunded", False)
    paymob_order_id = str(transaction.get("order", {}).get("id", ""))

    # Find the order in our database
    try:
        order = Order.objects.get(paymob_order_id=paymob_order_id)
    except Order.DoesNotExist:
        logger.error("Webhook: Order not found for paymob_order_id=%s", paymob_order_id)
        return HttpResponse(status=404)

    # Update order status
    if success and not is_voided and not is_refunded:
        order.status = "PAID"
        order.paid_at = timezone.now()
        order.save(update_fields=["status", "paid_at"])
        logger.info("Order %s marked as PAID via webhook.", order.id)
    else:
        order.status = "FAILED"
        order.save(update_fields=["status"])
        logger.info("Order %s marked as FAILED via webhook.", order.id)

    return HttpResponse(status=200)


# ── Paymob Callback (User Redirect) ───────────────────────────────


def paymob_callback(request):
    """
    GET endpoint for Paymob's 'Transaction Response Callback'.

    After payment, Paymob redirects the user's browser here with
    query parameters containing the result and HMAC.

    URL to configure in Paymob Dashboard:
        https://yourdomain.com/payment/callback/
    """
    success = request.GET.get("success", "false").lower() == "true"
    paymob_order_id = request.GET.get("order", "")

    # Verify HMAC from query params
    hmac_valid = paymob.verify_hmac_callback(request.GET)

    # Look up the order
    order = None
    if paymob_order_id:
        try:
            order = Order.objects.get(paymob_order_id=paymob_order_id)
        except Order.DoesNotExist:
            pass

    # Determine final result
    payment_success = success and hmac_valid

    context = {
        "payment_success": payment_success,
        "hmac_valid": hmac_valid,
        "order": order,
    }
    return render(request, "mainapp/payment_result.html", context)
