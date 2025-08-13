from datetime import datetime
from typing import Any

def format_timestamp(ts: float) -> str:
    """Formatea un timestamp float a string legible."""
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def validate_checksum(payload: bytes, expected_crc: int) -> bool:
    """Valida el checksum simple de un payload."""
    return (sum(payload[:-1]) & 0xFF) == expected_crc

def clamp(value: float, min_value: float, max_value: float) -> float:
    """Restringe un valor a un rango."""
    return max(min_value, min(value, max_value))
