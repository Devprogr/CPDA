import os
import requests

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM = os.getenv("RESEND_FROM_EMAIL")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
APP_BASE_URL = os.getenv("APP_BASE_URL")

def send_admin_new_event_email(event_id: str, title: str):
    if not (RESEND_API_KEY and RESEND_FROM and ADMIN_EMAIL and APP_BASE_URL):
        return

    approve_url = f"{APP_BASE_URL}/admin/events/{event_id}/approve"
    decline_url = f"{APP_BASE_URL}/admin/events/{event_id}/decline"

    html = f"""
      <div style="font-family: Arial, sans-serif; line-height:1.5">
        <h2>New Event Submission</h2>
        <p><b>{title}</b> has been submitted and is awaiting approval.</p>
        <p>
          <a href="{approve_url}">Approve</a> ·
          <a href="{decline_url}">Decline</a>
        </p>
      </div>
    """

    requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
        json={"from": RESEND_FROM, "to": [ADMIN_EMAIL], "subject": f"Approval Needed: {title}", "html": html},
        timeout=10,
    )