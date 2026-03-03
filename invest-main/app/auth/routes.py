import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from supabase import create_client

bp = Blueprint("auth", __name__, url_prefix="/auth")

SUPABASE_URL = os.getenv("SUPABASE_URL")
ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
sb = create_client(SUPABASE_URL, ANON_KEY)

@bp.get("/login")
def login_page():
    return render_template("auth/login.html")

@bp.post("/login")
def login_submit():
    email = request.form.get("email","").strip()
    password = request.form.get("password","")

    if not email or not password:
        flash("Please enter email and password.", "danger")
        return redirect(url_for("auth.login_page"))

    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        session["sb_access_token"] = res.session.access_token
        session["sb_user_id"] = res.user.id
        flash("Logged in.", "success")
        return redirect(url_for("events.submit_page"))
    except Exception:
        flash("Invalid login.", "danger")
        return redirect(url_for("auth.login_page"))

@bp.get("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("events.calendar_page"))