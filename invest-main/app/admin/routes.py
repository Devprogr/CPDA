import os
from datetime import datetime
from flask import Blueprint, render_template, session, abort, redirect, url_for, flash
from supabase import create_client
from app.auth.service import verify_access_token, get_profile

bp = Blueprint("admin", __name__, url_prefix="/admin")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
sb_admin = create_client(SUPABASE_URL, SERVICE_KEY)

def require_admin():
    user = verify_access_token(session.get("sb_access_token"))
    if not user:
        abort(403)
    profile = get_profile(user.id)
    if not profile or profile.get("role") != "admin":
        abort(403)
    return user

@bp.get("/events")
def dashboard():
    require_admin()
    pending = sb_admin.table("events").select("*").eq("status", "PENDING").order("created_at", desc=True).execute().data
    return render_template("admin/dashboard.html", pending=pending)

@bp.get("/events/<event_id>/approve")
def approve(event_id):
    require_admin()
    sb_admin.table("events").update({
        "status": "APPROVED",
        "decided_at": datetime.utcnow().isoformat()
    }).eq("id", event_id).execute()

    flash("Event approved.", "success")
    return redirect(url_for("admin.dashboard"))

@bp.get("/events/<event_id>/decline")
def decline(event_id):
    require_admin()
    sb_admin.table("events").update({
        "status": "DECLINED",
        "decided_at": datetime.utcnow().isoformat()
    }).eq("id", event_id).execute()

    flash("Event declined.", "warning")
    return redirect(url_for("admin.dashboard"))