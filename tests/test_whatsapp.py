"""
Phase 5 WhatsApp webhook tests — run directly: python -m tests.test_whatsapp
Sends simulated WhatsApp payloads and verifies the full pipeline.
"""
import httpx
import json

BASE_URL = "http://localhost:8004"

PAYLOADS = [
    {
        "label": "Hot WhatsApp lead",
        "payload": {
            "from": "+905551234567",
            "name": "Ahmet Yilmaz",
            "message": "Urgent: we need automation for our retail chain of 20 stores. Budget is ready, I am the owner.",
            "timestamp": "2024-01-15T10:30:00Z",
        },
        "expected_label": "hot",
    },
    {
        "label": "Warm WhatsApp lead",
        "payload": {
            "from": "+905559876543",
            "name": "Fatma Kaya",
            "message": "Hi, I run a mid-size healthcare clinic and I am interested in your automation services.",
            "timestamp": "2024-01-15T11:00:00Z",
        },
        "expected_label": "warm",
    },
    {
        "label": "Cold WhatsApp lead",
        "payload": {
            "from": "+905550001111",
            "name": "Unknown",
            "message": "hello",
            "timestamp": "2024-01-15T12:00:00Z",
        },
        "expected_label": "cold",
    },
]


def run_tests():
    print("=" * 60)
    print("Phase 5 - WhatsApp Webhook Tests")
    print("=" * 60)

    passed = 0
    for i, case in enumerate(PAYLOADS, 1):
        print(f"\n[{i}] {case['label']}")
        print(f"     From   : {case['payload']['from']}")
        print(f"     Message: {case['payload']['message'][:60]}")

        try:
            r = httpx.post(
                f"{BASE_URL}/api/whatsapp-webhook",
                json=case["payload"],
                timeout=40,
            )
            data = r.json()

            if r.status_code == 200:
                label = data["score"]["label"]
                score = data["score"]["score"]
                record_id = data["id"]
                status = "PASS" if label == case["expected_label"] else "WARN"
                if label == case["expected_label"]:
                    passed += 1
                print(f"     Score  : {score}")
                print(f"     Label  : {label}  (expected: {case['expected_label']})  [{status}]")
                print(f"     Airtable ID: {record_id}")
                print(f"     Source : whatsapp (check Airtable)")
            else:
                print(f"     ERROR {r.status_code}: {data}")

        except Exception as e:
            print(f"     EXCEPTION: {e}")

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{len(PAYLOADS)} matched expected labels")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
