"""
Phase 2 qualification tests — run directly: python tests/test_qualification.py
Tests 5 lead scenarios and prints score, label, reason for each.
"""
from app.models.schemas import LeadInput
from app.services.qualification import qualify_lead

TEST_CASES = [
    {
        "label": "HOT (VP with budget)",
        "lead": LeadInput(
            name="Sarah Miller",
            email="sarah@bigcorp.com",
            company="BigCorp",
            sector="Technology",
            message="We need a CRM system ASAP for our 50-person sales team. Budget approved at $50k. I'm the VP of Sales.",
        ),
        "expected": "hot",
    },
    {
        "label": "HOT (urgent cost problem)",
        "lead": LeadInput(
            name="James Park",
            email="james@startup.io",
            company="StartupIO",
            sector="Finance",
            message="Urgent: Looking for automation solution. We're losing $10k/month on manual processes. Can we meet this week?",
        ),
        "expected": "hot",
    },
    {
        "label": "WARM (exploring options)",
        "lead": LeadInput(
            name="Linda Chen",
            email="linda@midtech.com",
            company="MidTech",
            sector="Technology",
            message="Interested in your services. We're a mid-size tech company exploring options.",
        ),
        "expected": "warm",
    },
    {
        "label": "COLD (vague)",
        "lead": LeadInput(
            name="Unknown",
            email="unknown@mail.com",
            message="Just browsing. Maybe someday.",
        ),
        "expected": "cold",
    },
    {
        "label": "COLD (minimal)",
        "lead": LeadInput(
            name="Anonymous",
            email="anon@mail.com",
            message="hi",
        ),
        "expected": "cold",
    },
]


def run_tests():
    print("=" * 60)
    print("Phase 2 — Lead Qualification Tests")
    print("=" * 60)

    passed = 0
    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n[{i}] {case['label']}")
        print(f"     Message : {case['lead'].message[:70]}")

        result = qualify_lead(case["lead"])

        status = "PASS" if result.label == case["expected"] else "WARN"
        if result.label == case["expected"]:
            passed += 1

        print(f"     Score   : {result.score}")
        print(f"     Label   : {result.label}  (expected: {case['expected']})  [{status}]")
        print(f"     Reason  : {result.reason}")
        print(f"     Reply   : {result.suggested_response}")

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{len(TEST_CASES)} matched expected labels")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
