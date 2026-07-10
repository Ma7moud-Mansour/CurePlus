import requests

API_KEY = "YOUR_API_KEY_HERE"
INTEGRATION_ID = 5765623

headers = {
    "Authorization": f"Token {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "amount": 100,
    "currency": "EGP",
    "payment_methods": [INTEGRATION_ID],
    "special_reference": "test-3",
    "billing_data": {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@test.com",
        "phone_number": "01000000000",
        "apartment": "NA",
        "floor": "NA",
        "street": "NA",
        "building": "NA",
        "shipping_method": "NA",
        "postal_code": "NA",
        "city": "NA",
        "country": "EG",
        "state": "NA",
    }
}

try:
    r = requests.post(
        "https://accept.paymob.com/v1/intention/",
        json=payload,
        headers=headers,
        timeout=10,
    )
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
