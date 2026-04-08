"""
Check current date and timezone issues
"""
from datetime import datetime, timedelta
import pytz

# Current UTC time
now_utc = datetime.utcnow()
print(f"Current UTC time: {now_utc}")
print(f"Current UTC date: {now_utc.date()}")

# Check if today is Feb 1, 2026
today = now_utc.date()
expected_today = datetime(2026, 2, 1).date()
print(f"Expected today: {expected_today}")
print(f"Dates match: {today == expected_today}")

# Check the date range for daily revenue (last 7 days)
seven_days_ago = today - timedelta(days=7)
print(f"\n7-day range for daily revenue:")
print(f"From: {seven_days_ago}")
print(f"To: {today}")

# The paid invoices are from 2026-01-29
invoice_date = datetime(2026, 1, 29).date()
print(f"\nPaid invoice date: {invoice_date}")
print(f"Invoice date in range: {seven_days_ago <= invoice_date <= today}")

# Calculate days difference
days_diff = (today - invoice_date).days
print(f"Days difference: {days_diff} days ago")
