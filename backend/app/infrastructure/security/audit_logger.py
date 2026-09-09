import json
import logging
from typing import Any


logger = logging.getLogger("mde.audit")
logger.setLevel(logging.INFO)


def audit_event(
    event: str,
    *,
    actor_user_id: str | None = None,
    resource_id: str | None = None,
    outcome: str,
    correlation_id: str | None = None,
    ip_address: str | None = None,
) -> None:
    payload: dict[str, Any] = {
        "actor_user_id": actor_user_id,
        "correlation_id": correlation_id,
        "event": event,
        "ip_address": ip_address,
        "outcome": outcome,
        "resource_id": resource_id,
    }
    logger.info(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def audit_request_event(
    request: Any,
    event: str,
    *,
    actor_user_id: str | None = None,
    resource_id: str | None = None,
    outcome: str,
) -> None:
    client = getattr(request, "client", None)
    audit_event(
        event,
        actor_user_id=actor_user_id,
        resource_id=resource_id,
        outcome=outcome,
        correlation_id=getattr(request.state, "correlation_id", None),
        ip_address=getattr(client, "host", None),
    )
