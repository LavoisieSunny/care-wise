"""
Structured audit logging, loosely modeled on the Cloud Auditing Data
Federation (CADF) event shape: who did what, to which resource, when,
and whether it succeeded.

This is intentionally minimal -- it writes newline-delimited JSON to
stdout/a rotating file so it can be piped into any SIEM later. It is
NOT a substitute for a real 6-year retention/immutable audit trail;
it exists to demonstrate the *shape* of enterprise-grade audit logging
(observer, initiator, action, target, outcome) without pretending to
solve HIPAA's retention and tamper-evidence requirements, which need
real infrastructure (WORM storage, log signing) to do properly.
"""
import json
import logging
import time
import uuid
from typing import Optional, Any, Dict

audit_logger = logging.getLogger("carewise.audit")
audit_logger.setLevel(logging.INFO)
if not audit_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    audit_logger.addHandler(handler)


def record_event(
    action: str,
    target_type: str,
    target_id: Optional[str] = None,
    initiator_id: str = "anonymous",
    outcome: str = "success",
    detail: Optional[Dict[str, Any]] = None,
) -> None:
    """Emit one structured audit event.

    Example: record_event("policy.upload", "policy", policy_id,
                           initiator_id=request_ip, outcome="success")
    """
    event = {
        "id": str(uuid.uuid4()),
        "eventTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "action": action,
        "outcome": outcome,
        "initiator": {"id": initiator_id, "typeURI": "service/security/account/user"},
        "target": {"id": target_id or "n/a", "typeURI": f"data/{target_type}"},
        "detail": detail or {},
    }
    audit_logger.info(json.dumps(event, ensure_ascii=False))
