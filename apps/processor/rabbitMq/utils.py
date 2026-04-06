import datetime
from time import timezone


def calculate_delay_ms(target_date_str: str) -> str:
    target_date = datetime.strptime(target_date_str, "%d.%m.%Y %H:%M:%S").replace(tzinfo=timezone.utc)
    now = datetime.now(datetime.timezone.utc)
    
    delay_seconds = (target_date - now).total_seconds()
    
    if delay_seconds < 0:
        return "0"
        
    return str(int(delay_seconds * 1000))