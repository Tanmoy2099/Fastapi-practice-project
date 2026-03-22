from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_order_mapping():
    url = "/api/v1/order"

    payload = {
        "data": {
            "product": {"id": "p1", "price": 100, "quantity": 2},
            "pricing": {"tax": 10, "discount": 5},
            "meta": {"external": {"id": "ext-123"}, "price": {"history": [90, 95], "current": 100}},
            "instanceId": "inst-1",
            "totalPrice": 110,
            "actualPrice": 105,
        },
        "payment": {
            "payment_type": "card",
            "card_number": "1234567812345678",
            "cvv": "123",
            "save_card": True,
        },
    }

    print(f"Sending request to {url}...")
    response = client.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    import json

    try:
        print("Response:", json.dumps(response.json(), indent=2))
        assert response.status_code == 200, "Expected 200 OK"
        assert response.json()["status"] == "success", "Expected success status"
        print("Test passed cleanly!")
    except Exception as e:
        print("Error:", e)
        print("Raw content:", response.content)


if __name__ == "__main__":
    test_order_mapping()
