"""
Paymob payment gateway service module (Intention API v1).

Uses the new Paymob Intention API with secret key authentication.
Flow:
  1. Create a Payment Intention (single API call)
  2. Redirect user to Paymob Checkout using the client_secret
  3. Verify HMAC on webhook/callback
"""

import hashlib
import hmac
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

PAYMOB_BASE_URL = "https://accept.paymob.com"


# ── 1. Create Payment Intention ────────────────────────────────────


def create_intention(amount_cents, billing_data, merchant_order_id):
    """
    Create a payment intention with Paymob.

    This single API call replaces the legacy 3-step flow
    (authenticate → register order → payment key).

    Args:
        amount_cents: Total amount in **cents** (e.g. 60000 for 600 EGP).
        billing_data: Dict with keys: first_name, last_name, email,
                      phone_number.
        merchant_order_id: Our internal order UUID (as string).

    Returns:
        Dict with 'client_secret' and 'intention_id'.

    Raises:
        requests.HTTPError: If the API returns a non-2xx status.
    """
    payload = {
        "amount": amount_cents,
        "currency": "EGP",
        "payment_methods": [int(settings.PAYMOB_INTEGRATION_ID)],
        "billing_data": {
            "first_name": billing_data.get("first_name", "NA"),
            "last_name": billing_data.get("last_name", "NA"),
            "email": billing_data.get("email", "NA"),
            "phone_number": billing_data.get("phone_number", "NA"),
            # Required fields by Paymob – filled with "NA"
            "apartment": "NA",
            "floor": "NA",
            "street": "NA",
            "building": "NA",
            "shipping_method": "NA",
            "postal_code": "NA",
            "city": "NA",
            "country": "EG",
            "state": "NA",
        },
        "merchant_order_id": str(merchant_order_id),
        "items": [],
    }

    headers = {
        "Authorization": f"Token {settings.PAYMOB_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{PAYMOB_BASE_URL}/v1/intention/",
        json=payload,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    client_secret = data.get("client_secret")
    intention_id = data.get("id")
    logger.info(
        "Paymob intention created: id=%s for order %s",
        intention_id, merchant_order_id,
    )
    return {
        "client_secret": client_secret,
        "intention_id": intention_id,
    }


# ── 2. Checkout URL Builder ───────────────────────────────────────


def build_checkout_url(client_secret):
    """Build the Paymob Unified Checkout redirect URL."""
    return (
        f"https://accept.paymob.com/unifiedcheckout/?publicKey="
        f"{settings.PAYMOB_PUBLIC_KEY}&clientSecret={client_secret}"
    )


# ── 3. HMAC Verification ──────────────────────────────────────────

# The exact ordered list of fields Paymob uses to compute the HMAC.
# See: https://docs.paymob.com/docs/hmac-calculation
HMAC_FIELDS = [
    "amount_cents",
    "created_at",
    "currency",
    "error_occured",
    "has_parent_transaction",
    "id",
    "integration_id",
    "is_3d_secure",
    "is_auth",
    "is_capture",
    "is_refunded",
    "is_standalone_payment",
    "is_voided",
    "order",
    "owner",
    "pending",
    "source_data.pan",
    "source_data.sub_type",
    "source_data.type",
    "success",
]


def _extract_hmac_value(data, dotted_key):
    """
    Extract a value from a nested dict using a dotted key path.
    e.g. 'source_data.pan' → data['source_data']['pan']
    """
    keys = dotted_key.split(".")
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, "")
        else:
            return ""
    return value


def verify_hmac(data, received_hmac):
    """
    Verify the HMAC signature sent by Paymob (webhook JSON body).

    Args:
        data: The transaction data dict (the 'obj' from webhook JSON).
        received_hmac: The HMAC string sent by Paymob.

    Returns:
        True if the signature is valid, False otherwise.
    """
    concatenated = ""
    for field in HMAC_FIELDS:
        value = _extract_hmac_value(data, field)
        concatenated += str(value).lower() if isinstance(value, bool) else str(value)

    computed = hmac.new(
        settings.PAYMOB_HMAC_SECRET.encode("utf-8"),
        concatenated.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()

    is_valid = hmac.compare_digest(computed, received_hmac)
    if not is_valid:
        logger.warning("HMAC verification failed. Expected: %s, Got: %s", computed, received_hmac)
    return is_valid


def verify_hmac_callback(query_params):
    """
    Verify HMAC from the redirect callback query parameters.

    Args:
        query_params: Django QueryDict from request.GET.

    Returns:
        True if the signature is valid, False otherwise.
    """
    received_hmac = query_params.get("hmac", "")

    concatenated = ""
    for field in HMAC_FIELDS:
        value = query_params.get(field, "")
        concatenated += str(value)

    computed = hmac.new(
        settings.PAYMOB_HMAC_SECRET.encode("utf-8"),
        concatenated.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()

    is_valid = hmac.compare_digest(computed, received_hmac)
    if not is_valid:
        logger.warning("Callback HMAC verification failed.")
    return is_valid
