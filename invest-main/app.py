import os
import httpx
from flask import Flask, render_template, redirect, url_for, flash, session, request
from dotenv import load_dotenv
from supabase import create_client, Client
from contact_form import ContactForm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app():
    load_dotenv()

    app = Flask(
        __name__,
        static_folder=os.path.join(BASE_DIR, "static"),
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_url_path="/static"
    )

    # Secret key (Vercel: set APP_SECRET_KEY in env vars)
    app.secret_key = os.getenv("APP_SECRET_KEY") or os.getenv("FLASK_SECRET_KEY") or "dev_only_change_me"

    # Cookie security
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=True,  # HTTPS on Vercel
    )

    # Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
    if not supabase_url or not supabase_anon_key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment variables.")

    supabase: Client = create_client(supabase_url, supabase_anon_key)

    # Admin creds (set in Vercel env vars)
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "change_me")

    # ---------------- HELPERS ----------------

    def _is_member_logged_in() -> bool:
        return bool(session.get("member_access_token"))

    # ---------------- PUBLIC ROUTES ----------------

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/home-bkk")
    def homeBkk():
        return render_template("index_bkk.html")

    @app.route("/map")
    def map():
        return render_template("map.html")

    @app.route("/join")
    def join():
        return render_template("join.html")

    @app.route("/about-us")
    def aboutUs():
        return render_template("about-us.html")

    @app.route("/get-involved")
    def get_involved():
        return render_template("get-involved.html")

    @app.route("/news-updates")
    def news_updates():
        return render_template("news-updates.html")

    @app.route("/vision")
    def vision():
        return redirect("/about-us#vision", code=301)

    @app.route("/priorities")
    def priorities():
        return render_template("priorities.html")

    @app.route("/industries")
    def industries():
        return render_template("industries.html")

    @app.route("/agri-process")
    def agri_process():
        return render_template("agri-process.html")

    @app.route("/agriculture")
    def agriculture():
        return render_template("agriculture.html")

    @app.route("/mining")
    def mining():
        return render_template("mining.html")

    @app.route("/tourism")
    def tourism():
        return render_template("tourism.html")

    @app.route("/transportation")
    def transportation():
        return render_template("transportation.html")

    @app.route("/health-education")
    def health_education():
        return render_template("health-education.html")

    @app.route("/region")
    def region():
        years = ["2024", "2023", "2022", "2021"]
        populations = [86781, 86298, 86005, 86547]

        age_groups = [
            "85 years and over", "80 to 84 years", "75 to 79 years", "70 to 74 years",
            "65 to 69 years", "60 to 64 years", "55 to 59 years", "50 to 54 years",
            "45 to 49 years", "40 to 44 years", "35 to 39 years", "30 to 34 years",
            "25 to 29 years", "20 to 24 years", "15 to 19 years", "10 to 14 years",
            "5 to 9 years", "0 to 4 years"
        ]

        men = [-200, -300, -400, -500, -600, -700, -800, -900, -950, -1000, -950, -900, -850, -800, -750, -700, -650, -600]
        women = [250, 350, 450, 550, 650, 750, 850, 950, 1000, 1050, 1000, 950, 900, 850, 800, 750, 700, 650]

        income_labels = [
            "$200,000 and over", "$150,000 to 199,999", "$125,000 to 149,999", "$100,000 to 124,999",
            "$90,000 to 99,999", "$80,000 to 89,999", "$70,000 to 79,999", "$60,000 to 69,999",
            "$50,000 to 59,999", "$45,000 to 49,999", "$40,000 to 44,999", "$35,000 to 39,999",
            "$30,000 to 34,999", "$25,000 to 29,999", "$20,000 to 24,999", "$15,000 to 19,999",
            "$10,000 to 14,999", "$5,000 to 9,999", "Under $5,000"
        ]
        households_2024 = [716, 1535, 1321, 1554, 936, 915, 982, 1013, 1111, 678, 622, 675, 592, 633, 843, 337, 140, 62, 40]

        return render_template(
            "region.html",
            years=years,
            populations=populations,
            age_groups=age_groups,
            men=men,
            women=women,
            income_labels=income_labels,
            households_2024=households_2024
        )

    @app.route("/contact-us", methods=["GET", "POST"])
    def contact_us():
        contact_form = ContactForm()

        if contact_form.validate_on_submit():
            try:
                supabase.table("contact_messages").insert({
                    "name": contact_form.name.data,
                    "email": contact_form.email.data,
                    "message": contact_form.message.data
                }).execute()

                flash("Your message has been sent successfully!", "success")
                return redirect(url_for("contact_us"))
            except Exception as e:
                print("Supabase Error:", e)
                flash("Something went wrong. Please try again later.", "danger")

        return render_template("contact-us.html", form=contact_form)

    # ---------------- MEMBERS AUTH ----------------

    @app.route("/membership")
    def membership():
        return redirect(url_for("auth_login"), code=302)

    @app.route("/auth/login", methods=["GET", "POST"])
    def auth_login():
        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password") or ""

            if not email or not password:
                flash("Please enter email and password.", "danger")
                return render_template("auth/login.html")

            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})

                session["member_access_token"] = res.session.access_token
                session["member_refresh_token"] = res.session.refresh_token
                session["member_user"] = {"email": res.user.email, "id": res.user.id}

                flash("Logged in successfully.", "success")
                return redirect(url_for("event_submit"))
            except Exception as e:
                print("Login error:", e)
                flash("Login failed. Check your email/password.", "danger")

        return render_template("auth/login.html")

    @app.route("/auth/register", methods=["GET", "POST"])
    def auth_register():
        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password") or ""
            confirm = request.form.get("confirm_password") or ""

            if not email or not password:
                flash("Please enter email and password.", "danger")
                return render_template("auth/register.html")

            if password != confirm:
                flash("Passwords do not match.", "danger")
                return render_template("auth/register.html")

            try:
                supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options": {
                        "email_redirect_to": url_for("auth_callback", _external=True)
                    }
                })

                flash("Account created. Please check your email to confirm.", "success")
                return redirect(url_for("auth_login"))
            except Exception as e:
                print("Register error:", e)
                flash("Registration failed. Try a different email.", "danger")

        return render_template("auth/register.html")

    @app.route("/auth/callback")
    def auth_callback():
        code = request.args.get("code")
        if not code:
            flash("Invalid or expired confirmation link.", "danger")
            return redirect(url_for("auth_login"))

        try:
            res = supabase.auth.exchange_code_for_session({"auth_code": code})

            session["member_access_token"] = res.session.access_token
            session["member_refresh_token"] = res.session.refresh_token
            session["member_user"] = {"email": res.user.email, "id": res.user.id}

            flash("Email verified. You are now logged in.", "success")
            return redirect(url_for("event_submit"))
        except Exception as e:
            print("Callback error:", e)
            flash("Confirmation link expired or invalid.", "danger")
            return redirect(url_for("auth_login"))

    @app.route("/auth/logout")
    def auth_logout():
        session.pop("member_access_token", None)
        session.pop("member_refresh_token", None)
        session.pop("member_user", None)
        flash("Logged out.", "info")
        return redirect(url_for("auth_login"))

    # Optional dashboard (keep if you still want it)
    @app.route("/members/dashboard")
    def member_dashboard():
        if not _is_member_logged_in():
            flash("Please login to continue.", "warning")
            return redirect(url_for("auth_login"))

        user = session.get("member_user", {})
        return render_template("members/dashboard.html", user=user)

    # ---------------- EVENTS ----------------

    @app.route("/events")
    def events():
        return render_template("events/index.html")

    @app.route("/events/submit", methods=["GET", "POST"])
    def event_submit():
        if not _is_member_logged_in():
            flash("Please login to submit an event.", "warning")
            return redirect(url_for("auth_login"))

        if request.method == "POST":
            title = (request.form.get("title") or "").strip()
            date = (request.form.get("date") or "").strip()
            location = (request.form.get("location") or "").strip()
            description = (request.form.get("description") or "").strip()

            if not title or not date:
                flash("Please fill at least Title and Date.", "danger")
                return render_template("events/submit.html")

            try:
                supabase.table("events").insert({
                    "title": title,
                    "date": date,
                    "location": location,
                    "description": description,
                    "status": "pending",
                    "submitted_by": (session.get("member_user") or {}).get("email")
                }).execute()

                flash("Event submitted! Pending approval.", "success")
                return redirect(url_for("events"))
            except Exception as e:
                print("Event insert error:", e)
                flash("Could not submit event. Try again.", "danger")

        return render_template("events/submit.html")

    # ---------------- ADMIN ----------------

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            if username == admin_username and password == admin_password:
                session["admin_logged_in"] = True
                flash("Logged in as admin", "success")
                return redirect(url_for("contact_messages"))

            flash("Invalid credentials", "danger")

        return render_template("admin/login.html")

    @app.route("/admin/logout")
    def admin_logout():
        session.pop("admin_logged_in", None)
        flash("Logged out.", "info")
        return redirect(url_for("admin_login"))

    @app.route("/admin/contact-messages")
    def contact_messages():
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        try:
            response = supabase.table("contact_messages").select("*").order("id", desc=True).execute()
            messages = response.data
        except Exception as e:
            print("Admin messages error:", e)
            flash("Failed to load messages.", "danger")
            messages = []

        return render_template("admin/contact_message.html", messages=messages)

    return app


# Vercel entrypoint:
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)