"""
Phase 3 CRM tests — run directly: python -m tests.test_crm
Tests Airtable create, read, update, and stats operations.
"""
from app.models.schemas import LeadInput, LeadScore
from app.services.crm import create_lead, get_lead_stats, get_leads, update_lead


def run_tests():
    print("=" * 60)
    print("Phase 3 — Airtable CRM Tests")
    print("=" * 60)

    # Test 1: Create a lead
    print("\n[1] Creating test lead in Airtable...")
    lead = LeadInput(
        name="CRM Test User",
        email="crmtest@example.com",
        company="TestCorp",
        sector="Technology",
        message="Testing Airtable CRM integration from Phase 3.",
        source="web_form",
    )
    score = LeadScore(
        score=75,
        label="hot",
        reason="Test lead for CRM integration.",
        suggested_response="Thank you for your interest, we will be in touch!",
    )
    record_id = create_lead(lead, score)
    print(f"     Record created | id={record_id}")
    assert record_id.startswith("rec"), f"Expected record ID starting with 'rec', got: {record_id}"
    print("     PASS")

    # Test 2: Read leads back
    print("\n[2] Fetching all leads from Airtable...")
    records = get_leads()
    print(f"     Total records fetched: {len(records)}")
    assert len(records) >= 1
    print("     PASS")

    # Test 3: Filter by label
    print("\n[3] Fetching hot leads only...")
    hot_leads = get_leads(label="hot")
    print(f"     Hot leads count: {len(hot_leads)}")
    for r in hot_leads:
        assert r["fields"].get("Label") == "hot"
    print("     PASS")

    # Test 4: Update the record
    print("\n[4] Updating record status to 'contacted'...")
    update_lead(record_id, {"Status": "contacted", "FollowUpCount": 1})
    # Verify update
    updated = get_leads(status="contacted")
    ids = [r["id"] for r in updated]
    assert record_id in ids, f"Record {record_id} not found in contacted leads"
    print(f"     Status updated | id={record_id}")
    print("     PASS")

    # Test 5: Stats
    print("\n[5] Fetching lead stats...")
    stats = get_lead_stats()
    print(f"     Total : {stats['total']}")
    print(f"     Labels: {stats['by_label']}")
    print(f"     Status: {stats['by_status']}")
    assert stats["total"] >= 1
    print("     PASS")

    print("\n" + "=" * 60)
    print("All CRM tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
