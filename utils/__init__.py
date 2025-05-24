

from datetime import datetime


def sub_two_dates(dt1: datetime, dt2: datetime):
    try:
        sub = int((dt1 - dt2).total_seconds())
        if sub < 0: # is negative
            sub *= -1
        # print(f"difference in seconds?: {sub}")
        return sub
    except Exception as e:
        print(f"Subtracting two dates failed: {e}")