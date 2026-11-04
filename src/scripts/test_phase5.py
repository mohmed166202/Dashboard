"""
Automated Test Suite for Phase 5: Automated Sync & Webhook Integration.
Validates HMAC-SHA256 signature verification, push commit inspection,
and webhook event routing.
"""

import hashlib
import hmac
import json
from webhook_server import should_trigger_on_push, verify_signature


def test_hmac_verification():
    print("[TEST] Testing HMAC-SHA256 Signature Verification...")
    secret = "my_secret_token_123"
    payload = json.dumps({"action": "created"}).encode("utf-8")

    # Generate valid signature
    valid_sig = "sha256=" + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    assert verify_signature(payload, valid_sig, secret) is True
    print("  -> Valid signature: PASS")

    # Invalid signature
    invalid_sig = "sha256=1234567890abcdef"
    assert verify_signature(payload, invalid_sig, secret) is False
    print("  -> Invalid signature rejection: PASS")


def test_push_trigger_filter():
    print("[TEST] Testing Push Commit Trigger Filter...")

    # Push with README changes
    push_docs = {
        "commits": [
            {"added": ["docs/architecture.md"], "modified": ["README.md"], "removed": []}
        ]
    }
    assert should_trigger_on_push(push_docs) is True
    print("  -> Docs modification triggers sync: PASS")

    # Push with schema changes
    push_schema = {
        "commits": [
            {"added": [], "modified": ["prisma/schema.prisma"], "removed": []}
        ]
    }
    assert should_trigger_on_push(push_schema) is True
    print("  -> Schema modification triggers sync: PASS")

    # Push with irrelevant file (e.g. css or test)
    push_asset = {
        "commits": [
            {"added": ["assets/logo.png"], "modified": ["style.css"], "removed": []}
        ]
    }
    assert should_trigger_on_push(push_asset) is False
    print("  -> Irrelevant asset modification ignored: PASS")


def main():
    print("=" * 65)
    print("RUNNING PHASE 5 WEBHOOK & SYNC ENGINE VERIFICATION")
    print("=" * 65)

    test_hmac_verification()
    test_push_trigger_filter()

    print("\n" + "=" * 65)
    print(">>> ALL PHASE 5 CONTINUOUS SYNC TESTS PASSED SUCCESSFULLY! <<<")
    print("=" * 65)


if __name__ == "__main__":
    main()

