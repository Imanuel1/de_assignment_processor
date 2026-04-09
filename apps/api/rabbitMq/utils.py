from datetime import datetime, timezone


def calculate_delay_ms(target_date_str: str) -> int:
    if not target_date_str:
        return 0

    target_date = datetime.fromisoformat(target_date_str).replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    
    delay_seconds = (target_date - now).total_seconds()
    
    if delay_seconds < 0:
        return 0
        
    return int(delay_seconds * 1000)