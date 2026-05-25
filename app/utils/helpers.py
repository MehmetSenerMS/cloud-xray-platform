from datetime import datetime, timezone
import uuid


def generate_transaction_id() -> str:
    return str(uuid.uuid4())


def get_current_utc_datetime() -> str:
    return datetime.now(timezone.utc).isoformat()