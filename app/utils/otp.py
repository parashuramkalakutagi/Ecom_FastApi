from datetime import datetime, timezone, timedelta
import random


def generate_otp():
    return str(random.randint(1000, 9999))

def otp_expiry():
    return datetime.now(timezone.utc) + timedelta(minutes=5)