import os
import secrets
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, jsonify
from supabase import create_client
from app.auth.service import verify_access_token
from .service import send_admin_new_event_email

bp = Blueprint("events", __name__, url_prefix="/events")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
sb_admin = create_client(SUPABASE_URL, SERVICE_KEY)

ALLOWED_EXT = {"png", "jpg", "jpeg", "pdf"}
MAX_POSTER_MB = 5

def require_login():
    user = verify_access_token(session.get("sb_access_token"))
    if not user:
        abort(403)
    return user

@bp.get("/")
def calendar_page():
    return render_template("events/calendar.html")

@bp.get("/api")
def approved_events_api():
    # Public: only APPROVED
    rows = sb_admin.table("events") \
        .select("id,title,start_at,end_at,location,description,poster_url") \
        .eq("status", "APPROVED") \
        .order("start_at") \
        .execute().data

    return jsonify([{
        "id": r["id"],
        "title": r["title"],
        "start": r["start_at"],
        "end": r["end_at"],
        "extendedProps": {
            "location": r.get("location"),
            "description": r.get("description"),
            "poster_url": r.get("poster_url"),
        }
    } for r in rows])

@bp.get("/submit")
def submit_page():
    require_login()
    return render_template("events/submit.html")

@bp.post("/submit")
def submit_post():
    user = require_login()

    title = request.form.get("title","").strip()
    start_at = request.form.get("start_at","").strip()
    end_at = request.form.get("end_at","").strip() or None
    location = request.form.get("location","").strip()
    description = request.form.get("description","").strip()

    if not title or not start_at:
        flash("Title and start date/time are required.", "danger")
        return redirect(url_for("events.submit_page"))

    poster = request.files.get("poster")
    poster_path = None
    poster_url = None

    if poster and poster.filename:
        ext = poster.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXT:
            flash("Poster must be PNG, JPG, or PDF.", "danger")
            return redirect(url_for("events.submit_page"))

        poster_bytes = poster.read()
        if len(poster_bytes) > MAX_POSTER_MB * 1024 * 1024:
            flash("Poster file is too large (max 5MB).", "danger")
            return redirect(url_for("events.submit_page"))

        safe_name = f"{secrets.token_hex(16)}.{ext}"
        poster_path = f"{datetime.utcnow().strftime('%Y/%m')}/{safe_name}"

        sb_admin.storage.from_("event-posters").upload(
            poster_path,
            poster_bytes,
            {"content-type": poster.mimetype}
        )

        # If bucket is public:
        poster_url = sb_admin.storage.from_("event-posters").get_public_url(poster_path)

    inserted = sb_admin.table("events").insert({
        "owner_id": user.id,
        "title": title,
        "description": description,
        "location": location,
        "start_at": start_at,
        "end_at": end_at,
        "poster_path": poster_path,
        "poster_url": poster_url,
        "status": "PENDING"
    }).execute()

    event_id = inserted.data[0]["id"]
    send_admin_new_event_email(event_id, title)

    flash("Submitted! Your event will appear after admin approval.", "success")
    return redirect(url_for("events.submit_page"))